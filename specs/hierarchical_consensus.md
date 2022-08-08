Hierarchical Consensus Spec
===

> This document includes the latest version of the hierarchical consensus spec along with the relevant FIPs to be proposed to the Filecoin community.

## Revisions
- `2022-06-14`: Basic structure and WIP
- `2022-06-17`: Draft for up to cross-net messages.
- `2022-06-20`: Content resolution and atomic execution protocols. Detectable misbehaviors.
- `2022-06-21`: First draft with all sections and linking [FIP draft](https://hackmd.io/gBmBo6ChQ4ajqN8RtKdJ9A).
- `2022-07-04`: Internal review by ConsensusLab (see [PR](https://github.com/protocol/ConsensusLab/pull/113)).

### Spec Status Legend
| Spec state |	Label |
|------------|---------|
|Unlikely to change in the foreseeable future. |	Stable |
|All content is correct. Important details are covered. Pending review/audit. |	Reliable |
|All content is correct. Details are being worked on. |	Draft/WIP |
|Do not follow. Important things have changed. |	Incorrect |
|No work has been done yet. |	Missing |

## Spec Status

Each section of the spec must be stable and audited before it is considered done. The state of each section is tracked below.

- The **State** column indicates the stability as defined in the legend above.
- The **Reviewed** column shows information about if the section has been reviewed and the latest date and the specific team/individual responsible for the review (this should give a sense of the stability of the spec).
- **Discussion issue** links the issue/discussion where the design or review of the spec is being discussed.
- The **FIP** column specifies the FIP in which the corresponding section (protocol scheme) is included.

> So far, all of the sections marked as __FIP__ are included [in this same FIP](https://hackmd.io/gBmBo6ChQ4ajqN8RtKdJ9A). When we have more than one FIP, we'll link to the relevant links in each case.

| Section      | State     | Reviewed    | Discussion Issue | __FIP__ |
|--------------|-----------|-------------|------|-----|
| [Introduction](#Introduction "Introduction") | Reliable | No | |N/A |
[Architecture](#Architecture "Architecture")| Reliable| No | | __FIP__ |
[Subnet Actor (SA)](#Subnet-Actor-SA "Subnet Actor (SA)") | Reliable | No | | __FIP__|
[Subnet Coordinator Actor (SCA)](#Subnet-Coordinator-Actor-SCA "Subnet Coordinator Actor (SCA)") | Reliable | No | | __FIP__ |
[Consensus Interface](#Consensus-Interface) | Reliable | No | | __FIP__ |
[Lifecycle of a subnet](#Lifecycle-of-a-subnet "Lifecycle of a subnet") | Reliable | No | |N/A |
[Spawning and joining a subnet](#Spawning-and-joining-a-subnet "Spawning and joining a subnet") | Reliable | No | |__FIP__ |
[Leaving and killing a subnet](#Leaving-and-killing-a-subnet "Leaving and killing a subnet}") | Reliable | No | |__FIP__ |
[Handling the state of killed subnets.](#Handling-the-state-of-killed-subnets "Handling the state of killed subnets.") | Draft/WIP | | |__FIP__|
[Naming](#Naming "Naming") | Reliable | No | | __FIP__ |
[SubnetID](#SubnetID "SubnetID") | Reliable | No | |__FIP__ |
[Hierarchical Address](#Hierarchical-Address "Hierarchical Address") | Reliable | No | |__FIP__ |
[Checkpointing](#Checkpointing "Checkpointing") | Reliable | No | |__FIP__ |
[Checkpoint Commitment](#Checkpoint-Commitment "Checkpoint Commitment") | Reliable | No | | __FIP__ |
[Checkpoints data structure](#Checkpoints-data-structure "Checkpoints data structure") | Reliable | No | | __FIP__ |
[Cross-net messages](#Cross-net-messages "Cross-net messages") | Reliable | No | |__FIP__ |
[cross-net message pool](#cross-net-message-pool "cross-net message pool") | Reliable | No | |__FIP__ |
[cross-net message execution](#cross-net-message-execution "cross-net message execution") | Reliable | No | |__FIP__ |
[Minting and Burning native tokens](#Minting-and-burning-native-tokens-in-subnets) | Reliable | No | | __FIP__ |
[Top-down messages](#Top-down-messages "Top-down messages") | Reliable | No | |__FIP__ |
[Bottom-up messages](#Bottom-up-messages "Bottom-up messages") | Reliable | No | |__FIP__ |
[Path messages](#Path-messages "Path messages") | Reliable | No | |__FIP__|
[Subnet Content Resolution Protocol](#Subnet-Content-Resolution-Protocol "Subnet Content Resolution Protocol") | Reliable | No | |__FIP__ |
[Cross-net routing gas price](#Cross-net-routing-gas-price "Cross-net routing gas price") | WIP/Draft |   | |N/A |
[Resolution approaches](#Resolution-approaches "Resolution approaches") | Reliable | No | |__FIP__ |
[Data availability](#Data-availability "Data availability") | WIP/Draft |  | |N/A |
[Atomic Execution Protocol](#Atomic-Execution-Protocol "Atomic Execution Protocol") | Reliable | No | |__FIP__|
[Collateral and slashing](#Collateral-and-slashing "Collateral and slashing") | WIP/Draft |  | |N/A |
[Detectable misbehaviors](#Detectable-misbehaviors "Detectable misbehaviors") | WIP/Draft |   | |N/A |

## Introduction
At a high level, hierarchical consensus (HC) allows for incremental, on-demand blockchain scaling and simplifies the deployment of new use cases with clearly isolated security domains that provide flexibility for varied use cases.

Consensus, or establishing total order across transactions, poses a major scalability bottleneck in blockchain networks. This is particularly the case when all validators are required to process all transactions. Regardless of the specific consensus protocol implementation used, this makes blockchains unable to increase their performance by adding more participants (scale-out).

In traditional distributed computing, one possible approach to overcoming this limitation is to resort to the partitioning, or sharding, of state processing and transaction ordering. In a sharded system, the blockchain stack is divided into different groups -- called shards --, each operated by its own set of nodes, which keep a subset of the state and are responsible for processing a part of the transactions sent to the system.

The main challenge with applying traditional sharding to the Byzantine fault-tolerant context of the blockchain lies in the security/performance tradeoff. As miners are assigned to shards, there is a danger of diluting security when compared to the original single-chain (single-shard) solution. In both proof-of-work and proof-of-stake (PoS) blockchains, sharding may give the attacker the ability to compromise a single shard with only a  fraction of the mining power, potentially compromising the system as a whole. Such attacks are often referred to as _1\% attacks_ [[1](https://ieeexplore.ieee.org/document/8510588), [2](https://dl.acm.org/doi/10.1145/2976749.2978389)]. To circumvent them, sharding systems need to periodically reassign miners to shards in an unpredictable way, so as to cope with a semi-dynamic adversary. We believe that this traditional approach to scaling, which considers the system as a monolith, is not suitable for decentralized blockchains due to their complexity.  <!--and the fact that sharded systems reshuffle state without the consent of its owners, disrupting use cases that benefit from finer control over the system topology.-->

With __[Hierarchical Consensus](https://research.protocol.ai/publications/hierarchical-consensus-a-horizontal-scaling-framework-for-blockchains/)__, we depart from the traditional sharding approach and instead of algorithmically assigning node membership and load balancing the distribution of the state, we follow an approach where users and miners freely self-select into subnets. Users (i.e. network participants) can spawn new independent networks, or child subnets, from the one they are operating in. __Each subnet can run its own independent consensus algorithm and set its own security and performance guarantees.__ Subnets in the system are organized hierarchically: each has one parent subnet and any number of child subnets, except for the root subnet (called _root network_ or _rootnet_), which has no parent and is the initial anchor of trust. Subnets can semlessly communicate and interact with state hosted in other subnets through cross-net messages.

To mitigate the 1\% attacks pertinent to traditional sharding, subnets in hierarchical consensus are [firewalled](https://ieeexplore.ieee.org/abstract/document/8835275), in the sense that the effects of a security violation in a given subnet are limited to that particular subnet and its children, with bounded economic impact on its ancestors. This bounded impact of an attack is, at most, the circulating supply of the parent token in the child subnet. Moreover, ancestor subnets help secure their descendant subnets through _checkpointing_, which helps alleviate attacks on a child subnet, such as long-range and related attacks in the case of a PoS-based subnet.

### Glossary
For clarity, we include here a glossary of HC-related concepts used throughout the spec:
- __Subnet__: Hierarchical consensus network that keeps its own independent state, consensus algorithm, message pool, and broadcast layer, but that is able to seamlessly interact and communicate with other subnets in the hierarchy.
- __Rootnet__: First network from which all new subnets are spawned and the hierarchy is built. In our case, the Filecoin mainnet.
- __Parent Subnet__: Network from which a new subnet (child) is spawned. The parent is the anchor of trust in the hierarchy for all of its children.
- __Peer/Node of a subnet__: A full node participating in a specific subnet (i.e. a member of the subnet syncing its full state).
- __Validator__: Peer of the subnet with the right to propose new blocks and to participate in the block validation protocol.
- __User/Client of a subnet__: Light node of a subnet (i.e. participant but not necessarily syncing the full state of the subnet).
- __Native Token__: Rootnet token, used for the interaction with the HC protocol. In our case, `FIL`.
- __Circulating Supply__: Number of native tokens transferred into a subnet for use therein.
- __Cross-net messages__: Messages originated in a subnet and directed to some other subnet in the hierarchy.
- __Collateral__: Amount of native tokens staked in a subnet's parent by the subnet's validators. This stake is slashed when a misbehavior in the subnet is detected and successfully reported to the parent.

## Architecture
The system starts with a _rootnet_ which, at first, keeps the entire state and processes all the transaction in the system (like present-day Filecoin). Any subset of users of the rootnet can spawn a new subnet from it.

> High-level architecture of hierarchical consensus
> ![](https://hackmd.io/_uploads/BJVIhk8Fc.png)

This subnet instantiates a new network with its own state, independent from the root network, replicated among the subset of participants of the overall system who are members of the subnet. From this point on, the new subnet processes transactions involving the state in the subnet independently of the root chain. Further subnets can then be spawned from any point in the hierarchy.

From the perspective of a peer in the network, spawning or syncing with a new subnet starts a set of new processes to handle the independent state, mempool, and the specific [GossipSub](https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.1.md) topic to broadcast and receive subnet-specific messages.

> Stack of an HC node
> ![](https://hackmd.io/_uploads/BJla0JLYq.png)

Subnets are able to interact with the state of other subnets (and that of the rootnet) through _[cross-subnet](#Cross-net-messages "Cross-net messages")_ (or, simply,  _cross-net_) messages. __Full nodes and validators in a given subnet need trusted access to the state of its parent subnet.__ We implement this by having them synchronise the chain of the parent subnet (i.e. child subnet full nodes also run full nodes on the parent subnet).

As it may be hard to enforce an honest majority of validators in every subnet, which can result in the subnet chain being compromised or attacked, the system provides a __firewall security property__. This guarantees that, for token exchanges, the impact of a child subnet being compromised is limited, in the worst case, to its circulating supply of the native token, determined by the (positive) balance between cross-net transactions entering the subnet and cross-net transactions leaving the subnet. Addresses in a subnet are funded through cross-net transactions that inject tokens into the subnet. In order for users to be able to spawn a new subnet, they need to deposit __initial collateral__ at the new subnet's parent. This collateral offers a minimum level of trust to new users injecting tokens into the subnet and can be slashed in case of misbehavior by subnet validators.

Validators in subnets are rewarded with fees for the transactions executed in the subnet. Subnets can run any consensus algorithm of their choosing, provided it can meet a defined interface, and they can determine the consensus proofs they want to include for light clients (i.e. nodes that do not synchronize and retain a full copy of the blockchain and thus do not verify all transactions). Subnets periodically commit a proof of their state in their parent through [checkpoints](#Checkpointing "Checkpointing"). These proofs are propagated to the top of the hierarchy, making them accessible to any member of the system. A checkpoint should include enough information that any client receiving it is able to verify the correctness of the subnet consensus. Subnets are free to choose a proof scheme that suits their consensus best (e.g. multi-signature, threshold signature, SPV (Simple Verification) or ZK (zero-knowledge) proofs, etc.). With this, users are able to determine the level of trust over a subnet according to the security level of the consensus run by the subnet and the proofs provided to light clients. Checkpoints are also used to propagate the information pertaining to cross-net messages to other subnets in the hierarchy.

The two key modules that implement the logic for hierarchical consensus are:
- __[Subnet Actor (SA)](#Subnet-Actor-SA "Subnet Actor (SA)")__: A user-defined actor deployed in the parent subnet from which the subnet wants to be spawned and that implements the subnet actor interface with the core logic and governing policies for the operation of the subnet.
- __[The Subnet Coordinator Actor (SCA)](#Subnet-Coordinator-Actor-SCA "Subnet Coordinator Actor (SCA)")__: A system actor deployed in the genesis of every HC-compatible subnet. The SCA implements the logic of the HC protocol and handles all the interactions with the rest of the system. It is included as an additional built-in actor in the built-in actors bundle.

> Snapshot of three subnets with their corrsponding actors.
> ![](https://hackmd.io/_uploads/ByfPG7IYq.png)

The reference implementations of both actors in Filecoin currently target the FVM. The SCA is implemented as an additional `builtin-actor` while SA is an FVM user-defined actor.

## Subnet Actor (SA)
The `SubnetActor` interface defines the core functions and basic rules required for an actor to implement the logic for a new subnet. This approach gives users total flexibility to configure the consensus, security assumption, checkpointing strategy, policies, etc. of their new subnet, so that it fulfils the needs of their use case.

The subnet actor is the public contract accessible by users in the system to determine the kind of child subnet being spawned and controlled by the actor. From the moment the SA for a new subnet is spawned in the parent chain, users looking to participate in the subnet can instantiate the new chain and even start mining on it. However, in order for the subnet to be able to interact with the rest of the hierarchy, it needs to be registered by staking an amount of native tokens over the `CollateralThreshold` in the parent's SCA _(see [Collateral and slashing](#Collateral-and-slashing "Collateral and slashing"))_.

#### Subnet actor interface
We provide a reference implementation of the subnet actor interface, but users are permitted to implement custom governing policies and mechanics that better suit their needs (e.g. request dynamic collateral for validators, add a leaving fee coefficient to penalize validators leaving the subnet before some time frame, require a minimum number of validators, include latency limits, etc.).

#### SubnetActor state
> Example of state of the subnet actor from the reference implementation.
```go
type SubnetState struct {
    // Human-readable name of the subnet.
    Name string
    // ID of the parent subnet
    ParentID SubnetID
    // Type of consensus algorithm.
    Consensus hierarchical.ConsensusType
    // Minimum collateral required for an address to join the subnet
    // as a miner
    MinMinerCollateral TokenAmount
    // Total collateral currently deposited in the
    // SCA from the subnet
    TotalStake TokenAmount
    // BalanceTable with the distribution of stake by address
    // This CID points to a HAMT where the key is the address of
    // the validator, and the value the amount of tokens staked
    // by the validator.
    Collateral Cid<HAMT<Address, TokenAmount>>
    // State of the subnet (Active, Inactive, Terminating)
    Status Status
    // Genesis bootstrap for the subnet. This is created
    // when the subnet is generated.
    Genesis []byte
    // Checkpointing period. Number of epochs between checkpoint commitments
    CheckPeriod ChainEpoch
    // Checkpoints submitted to the SubnetActor per epoch
    // This CID points to a HAMT where the key is the epoch
    // of the committed checkpoint, and the value the
    // the corresponding checkpoint.
    Checkpoints Cid<HAMT<ChainEpoch, Checkpoint>>
    // Validator votes for the checkpoint of the current window.
    // The CID points to a HAMT where the keys are the CID of the
    // checkpoint being voted in the current window and the value
    // the list of addresses of validators that have voted for
    // that checkpoint.
    CheckpointVotes Cid<HAMT<Cid, []Address>>
    // List of validators in the subnet
    ValidatorSet []hierarchical.Validator
    // Minimal number of validators required for the subnet
    // to be able to validate new blocks.
    MinValidators uint64
}
```
#### Constructor Parameters
> Constructor parameters for the reference implementation of the subnet actor.
```go
type ConstructParams struct {
    // ID of the current network
    NetworkName     SubnetID
    // Human-readable name for the subnet
    Name            SubnetID
    // Consensus implemented in the subnet
    Consensus hierarchical.ConsensusType
    // Arbitrary consensus parameters required to initialize
    // the consensus protocol (e.g. minimum number of validators).
    // These parameters are consensus-specific and they may change
    // for different implementations of the subnet actor.
    ConsensusParams *hierarchical.ConsensusParams
    // Minimum amount of collateral required from participant
    // to become a validator of the subnet.
    MinValidatorCollateral  TokenAmount
    // Checkpointing period used in the subnet. It determines
    // how often the subnet propagates and commits checkpoints in its
    // parent
    CheckPeriod     ChainEpoch
}
```
> TODO: There is an on-going revision of `ConstructParams` to include a way to provide arbitrary input arguments to a subnet.
> Interface every subnet actor needs to implement. These functions
> are triggered when a `message` is sent for their corresponding `methodNum`.
```go
type SubnetActor interface{
    // Initializes the state of the subnet actor and sets
    // all its initial parameters.
    //
    // - methodNum: 1
    // - allowed callers: any account.
    // - impacted state: SubnetState for the subnet actor
    // is initialized.
    // - side-effect message triggered: none
    Constructor(ConstructParams)

    // It expects as `value` the amount of collateral the
    // source wants to stake to become part of the subnet.
    // It triggers all check to determine if the source is eligible
    // to become part of the subnet, and must propagate an `AddCollateral` message
    // to the SCA to trigger the registration.
    //
    // Join is also responsible to send a `Register` message to the SCA
    // whenever the `CollateralThreshold` is reached. This function can also
    // be used to AddCollateral for the subnet in the SCA. Additional
    // checks for this operation may be included. As a result of the
    // execution an `AddCollateral` message must be sent to the SCA
    // including the added collateral.
    //
    // - methodNum: 2
    // - allowed callers: any account.
    // - impacted state: increases `TotalCollateral` with the `value` provided
    // in the message and updates the `Collateral` for the source of the message.
    // It updates the `Status` of the subnet
    // - side-effect message triggered:
    //    - Register() to SCA `TotalCollateral > CollateralThreshold` and subnet
    //    not registered
    //    - AddCollateral() to SCA including the amount of collateral included
    //    in the value of the message.
    // - invariants:
    //    - `Status` is `Active` iff `TotalColateral > CollateralThreshold`.
    Join()

    // Called by participants that want to leave the subnet. It triggers all
    // the checks to see if the source is eligible to leave the subnet.
    // This function must propagate a `ReleaseCollateral` message to the SCA.
    // The SCA will then release the corresponding stake of the validator in
    // a message to the subnet actor so the subnet actor can trigger a message
    // returning the funds to the leaving validtor.
    //
    // - methodNum: 3
    // - allowed callers: any validator with some collateral in the subnet.
    // - impacted state: reduces the `TotalCollateral` with the `value` provided
    // in the message and updates the `Collateral` for the source of the message.
    // It updates the `Status` of the subnet
    // - side-effect message triggered:
    //    - ReleaseCollateral() to SCA including the amount of collateral included
    //    in the value of the message.
    //    - Send() to the source of the message returning to the validator address
    //    the corresponding amount of tokens determined by the leaving policy.
    // - invariants:
    //    - `Status` is `Active` iff `TotalColateral > CollateralThreshold`.
    Leave()

    // Kill performs all the sanity-checks required before completely
    // killing (e.g. check that all validators have released
    // their stake, or that there are no user-funds left in the subnet's
    // state). It must propagate a `Kill` message to the SCA
    // to unregister the subnet from the hierarchy, making it no longer
    // discoverable.
    //
    // - methodNum: 4
    // - allowed callers: any account
    // - impacted state: It sets the `Status` of the subnet to killed.
    // - side-effect message triggered:
    //    - ReleaseCollateral() to SCA including the amount of collateral included
    //    in the value of the message.
    //    - Send() to the source of the message returning to the validator address
    //    the corresponding amount of tokens determined by the leaving policy.
    Kill()

    // SubmitCheckpoint is called by validators looking to submit a
    // signed checkpoint for propagation. This function performs all the
    // subnet-specific checks required for the final commitment of the
    // checkpoint in the SCA (e.g. in the reference implementation of
    // the SubnetActor, SubmitCheckpoints waits for more than 2/3 of the validators
    // to sign a valid checkpoint to propagate it to the SCA).
    //
    // This function must propagate a `CommitChildCheckpoint` message to the SCA
    // to commit the checkpoint.
    //
    // - methodNum: 5
    // - allowed callers: any validator with some collateral in the subnet.
    // - impacted state: It updates `CheckpointVotes` with the checkpoint and
    //   address of the validator submitting the checkpoint. It also updates
    //   `Checkpoints` if the signature policy to commit a checkpoint is fulfilled
    //   (+2/3 votes in the reference implementation).
    // - side-effect message triggered:
    //    - CommitChildCheckpoint() to SCA including the checkpoint that fulfilled
    //      the acceptance policy (e.g. +2/3 votes from validators)
    SubmitCheckpoint(Checkpoint)

    // CheckEquivocation is called by the SCA to perform consensus-specific
    // checks when an agreement equivocation is reported. It receives as input
    // the chain of the last `finality_delay` blocks including the invalid
    // blocks and the chain with what is supposed to be the valid block.
    //
    // - methodNum: 6
    // - allowed callers: any account
    // - impacted state: none
    // - side-effect message triggered: none
    CheckEquivocation(invalid []Block, valid []Block)
}
```

## Subnet Coordinator Actor (SCA)
The main entity responsible for handling all the lifecycle of child subnets in a specific chain is the subnet coordinator actor (`SCA`). The `SCA` is a built-in actor that exposes the interface for subnets to interact with the hierarchical consensus protocol. This actor includes all the available functionalities related to subnets and their management. It also enforces all the security requirements, fund management, and cryptoeconomics of hierarchical consensus, as subnet actors are user-defined and can't be (fully) trusted. The `SCA` has a reserved address ID `f064`.

The MVP implementation of this built-in actor can be found [here](https://github.com/adlrocha/builtin-actors/tree/master/actors/hierarchical_sca). The `SCA` exposes the following functions:

#### SCA State
> State of the SCA
```go
type SCAState struct {
    // ID of the current network
    NetworkName SubnetID
    // Number of active subnets spawned from this one
    TotalSubnets uint64
    // Minimum stake required to create a new subnet
    CollateralThreshold TokenAmount
    // List of subnets
    // The Cid points to a HAMT that keeps as keys the SubnetIDs of the
    // child subnets registered, and as values the corresponding Subnet
    // information.
    Subnets Cid<HAMT<SubnetID, Subnet>>
    // Checkpoint period in number of epochs for the subnet
    CheckPeriod ChainEpoch
    // Checkpoint templates in the SCA per epoch
    // This CID points to a HAMT where the key is the epoch
    // of the committed checkpoint, and the value the
    // the corresponding checkpoint.
    Checkpoints Cid<HAMT<ChainEpoch, Checkpoint>>
    // CheckMsgMetaRegistry
    // Stores information about the list of messages and child msgMetas being
    // propagated in checkpoints to the top of the hierarchy.
    // The CID points to a HAMT that tracks the CID of all the `CrossMsgs`
    // propagated in checkpoints from the subnet
    CheckMsgsRegistry Cid<HAMT<Cid, CrossMsgs>>
    // Latest nonce of a cross message sent from subnet.
    Nonce             uint64
    // Nonce of bottom-up messages for msgMeta received from checkpoints.
    // This nonce is used to mark with a nonce the metadata about cross-net
    // messages received in checkpoints. This is used to order the
    // bottom-up cross-net messages received through checkpoints.
    BottomUpNonce     uint64
    // Queue of bottom-up cross-net messages to be applied.
    BottomUpMsgsMeta  Cid // AMT[CrossMsgs]
    // AppliedNonces keep track of the next nonce of the message to be applied.
    // This prevents potential replay attacks.
    AppliedBottomUpNonce uint64
    AppliedTopDownNonce  uint64
    // Registry with all active atomic executions being orchestrated
    // by the current subnet.
    // The CID points to a HAMT that with keys the CIDs that uniequely
    // identify active atomic execution, and value the corresponding
    // information for the atomic execution.
    AtomicExecRegistry Cid<HAMT<Cid, AtomicExec>> // HAMT[cid]AtomicExec
}
```

> Struct with the information the SCA keeps for each child subnet
```go
// Subnet struct kept by the SCA with the information of
// all of its children.
type Subnet struct {
    // ID of the Subnet
    ID          SubnetID
    // Parent ID
    ParentID    SubnetID
    //  Collateral staked for this subnet.
    Collateral       TokenAmount
    // List of cross top-down messages committed for the subnet..
    TopDownMsgs Cid // AMT[ltypes.Messages]
    // Latest nonce of cross message submitted to subnet.
    Nonce      uint64
    // Amount of native tokens injected in the subnet and
    // that can be used freely in the subnet.
    CircSupply TokenAmount
    // Status of the checkpoint (`Active`, `Inactive`, etc.)
    Status     Status
    // Latest checkpoint committed for the subnet.
    // Kept for verification purposes.
    PrevCheckpoint Checkpoint
}
```

#### Checkpoints data structure
Checkpoints are always identified though the [Content Identifier (CID)](https://github.com/multiformats/cid) of their `Data` (i.e. the payload of the checkpoint), and they can optionally include the corresponding signature from validators in the subnet chain (this can be the signature of an individual miner, a multi-signature, or a threshold signature, depending on the `SA` policy). The signature is never used for the computation of the CID of the checkpoint.

> Checkpoints Data Structure
```go

// Checkpoints wrap the checkpoint data and
// a field dedicated for the arbitrary signing policy
// used by the subnet.
type Checkpoint struct {
    Data CheckpointData
    Sig []byte
}

// Data included in checkpoints
type CheckpointData struct {
    // The SubnetID of the subnet that is committing the checkpoint.
    // The `SCA` checks that the right subnet actor is committing
    //the checkpoint for the source to prevent forged checkpoints.
    Source     SubnetID
    // The proof of the state of the subnet that is to be
    // committed in the parent chain. In the reference
    // implementation of the subnet actor, we just include the
    // block for the epoch being committed, but this proof could
    // be a snapshot of a test, a ZK Proof, or any other piece of
    // information that subnets want to anchor in their parent's chain.
    Proof     []byte
    // Epoch of the checkpoint being committed.
    // The epoch must be a multiple of `CheckPeriod`.
    Epoch     ChainEpoch
    // Cid of the previous checkpoint committed for the subnet.
    PrevCheck Cid<Checkpoint>
    // Array with the aggregation of all the checkpoints committed
    // from the subnet's children.
    Children  []ChildCheck
    // Metadata of all the messages being propagated in the checkpoint.
    // This metadata includes the source, destination
    // and `CID` of the messages.
    CrossMsgs []CrossMsgMeta
}

// Package with all checkpoints committed in
// the checkpoint window from children.
type ChildCheck struct {
    // Source of the checkpoints. ID of the child.
    Source SubnetID
    // List of cid of the checkpoints committed by
    // the child in this checkpoint window.
    // TODO: Checkpoints are being propagated without
    // any aggregation. This will change soon and the spec
    // will be updated accordingly
    // (see https://github.com/filecoin-project/eudico/issues/217)
    Checks []Cid<Checkpoint>
}

// Metadata pointing to the list of messages being
// propagated in the checkpoint.
type CrossMsgMeta struct {
    // Source of the cross-net messages included in
    // this metadata package
    From    SubnetID
    // Destination of the cross-net messages included.
    To      SubnetID
    // CID of the aggregation of all the messages being
    // propagated. This CID is used to uniquely identify
    // this package of messages.
    MsgsCid Cid<CrossMsgs>
    // Nonce of the crossMsgMeta. It is used for partial
    // ordering and to prevent replay attacks.
    Nonce   uint64
    // Aggregation of all the native tokens being transacted
    // in the included messages.
    Value   TokenAmount
}

// CrossMsgs is the data structure used to persist in the
// `CrossMsgsRegistry` the `Msgs` and `CrossMsgMeta`
// propagated in checkpoints
type CrossMsgs struct {
    // Raw msgs from the subnet
    Msgs  []Message
    // Metas propagated from child subnets and included
    // in a checkpoint
    Metas []CrossMsgMeta
}

// MetaTag is a convenient struct
// used to compute the CID of the MsgMeta
type MetaTag struct {
    MsgsCid  Cid<[]Message>
    MetasCid Cid<[]CrossMsgMeta>
}
```
Every `CrossMsgMeta` gets updated with every new checkpoint on its way up the hierarchy aggregating messages with the same destination building a tree of linked message digests with different sources but the same destination. Thus, every subnet only sees the message aggregation of its children (i.e. the digest of all the subnet's children's CrossMsgMeta list). Any subnet looking to know the specific messages behind the `CID` of a `CrossMsgMeta` -- which will be the case for the destination subnet of the messages, see [cross-net messages](#cross-net-messages) -- only needs to send a query message leveraging the [Subnet Content Resolution Protocol](#Subnet-Content-Resolution-Protocol "Subnet Content Resolution Protocol") for the cross-net message `CID` to the corresponding pubsub topic of the source subnet.

> TODO: Add a figure of how `CrossMsgMeta` are aggregated?

#### SCA Functions and parameters
> Parameters and data types for SCA
```go
// Parameters called when initializing the SCA in genesis.
type ConstructParams struct {
    // ID of the current network.
    NetworkName SubnetID
    // Checkpoint period used in the subnet.
    CheckPeriod ChainEpoch
}

// Parameters of SendCross() with information about the
// cross-message to be sent.
type CrossMsgParams struct {
    // Message to be sent as a cross-message.
    Msg Message
    // Destination subnet for the cross-message.
    Destination SubnetID
}

// Parameters to initialize an atomic execution.
type AtomicExecParams struct {
    // See [Atomic Execution Protocol](#Atomic-Execution-Protocol]
    // section.
    //...
}

// Parameters to return the result of an atomic execution.
type SubmitExecParams struct {
    // See [Atomic Execution Protocol](#Atomic-Execution-Protocol]
    // section.
    //...
}
```

> Functions of the SCA. These functions are triggered when a `message` is sent for their corresponding `methodNum`.
```go
type SCA interface{
    // Initializes the state of the SCA and sets
    // all its initial parameters.
    //
    // - methodNum: 1
    // - allowed callers: system actor address (SCA is a builtin)
    //   actor and initialized in genesis.
    // - impacted state: it initializes the state of the SCA.
    // - side-effect message triggered: none
    Constructor(ConstructParams)

    // Register expects as source the address of the subnet actor of
    // the subnet that wants to be registered. The message's `value`
    // is the subnet's collateral and must exceed the `CollateralThreshold`.
    // This functions activates the subnet. From then on, other
    // subnets in the system are allowed to interact with it and the
    // subnet can start commtting its checkpoints.
    //
    // - methodNum: 2
    // - allowed callers: subnet actor addresses.
    // - impacted state: It updates `TotalSubnets` and initializes
    // a new `Active` subnet in the `Subnets` HAMT.
    // - side-effect message triggered: none
    Register()

    // AddCollateral expects as source the address of the subnet actor
    // for which the collateral wants to be added.  Its `value` should
    // include the amount of collateral to be added for the subnet.
    //
    // - methodNum: 3
    // - allowed callers: subnet actor addresses.
    // - impacted state: Updates the value of `Collateral` for the
    //   subnet that called the method.
    // - side-effect message triggered: none
    AddCollateral()

    // ReleaseCollateral expects as source the address of the subnet actor
    // for which the collateral should be released. It triggers a transfer message
    // to the subnet actor returning the corresponding collateral.
    //
    // - methodNum: 4
    // - allowed callers: subnet actor addresses.
    // - impacted state: Updates the value of `Collateral` for the
    //   subnet that initiated the message call.
    // - side-effect message triggered:
    //    - Send() message to the subnet actor that called the method including
    //    the amount of collateral released in its `value`
    ReleaseCollateral(value TokenAmount)

    // Kill expects as source the address of the subnet actor to be killed.
    // This function can only be executed if no collateral or circulating
    // supply is left for the subnet (i.e. balance = 0).
    //
    // - methodNum: 5
    // - allowed callers: subnet actor addresses.
    // - impacted state: Removes the subnet information for the subnet that
    //   called the method from the `Subnets` HAMT, and decrements `TotalSubnets`.
    // - side-effect message triggered: none
    // - invariants: The total balance of native tokens of a killed subnet should be zero·
    Kill()

    // CommitChildCheckpoint expects as source the address of the subnet actor for which the
    // checkpoint is being committed. The function performs some basic checks
    // to ensure that checkpoint is valid and it persist it in the SCA state.
    //
    // - methodNum: 6
    // - allowed callers: subnet actor addresses.
    // - impacted state: Updates `Checkpoint` including in the checkpoint template
    //  for the current window the CID of the child checkpoint committed, and any outstanding
    //  `CrossMsgMeta` to be propagated further. It updates
    //  `Subnet.PrevCheckpoint` for the subnet calling the method. It adds new top-down or
    //  bottom-up messages to `Subnet.TopDownMsgs` and `BottomUpMsgMeta`, respectively.
    // - side-effect message triggered: none
    // - invariants:
    //   - The checkpoint is only accepted if `Subnet.PrevCheckpoint` and
    //    `Checkpoint.Epoch > Subnet.PreviousCheckpoint.Epoch` and `Subnet.Status = Active`
    //   - For bottom-up messages to be propagated, `sum(CrossMsgsMeta.Value) < Subnet.CircSupply`.
    CommitChildCheckpoint(ch Checkpoint)

    // Fund can be called by any user in a subnet and it injects
    // the `value` of native tokens included in the message to the source's address in
    // the child subnet given as argument.
    //
    // - methodNum: 7
    // - allowed callers: any account
    // - impacted state: Append the fund message to the `TopDownMsgs` of the Subnet. Update
    //   of `CircSupply` for the subnet specified as parameter in the method.
    // - side-effect message triggered:
    //   - ResolvePubKey() message to the address of account actor that called this method.
    Fund(SubnetID)

    // Release can be called by any user in a subnet to release the amount
    // of native tokens included in `value` from its own address in the
    // subnet to the address in the parent.
    //
    // - methodNum: 8
    // - allowed callers: any account
    // - impacted state: Update `Checkpoint` to include in its `CrossMsgMeta` a
    //  `CrossMsgs` with this new release message and an updated `Value`.
    //  It also triggers an update of `CheckMsgsRegistry` with the updated `CrossMsgs`.
    // - side-effect message triggered:
    //   - ResolvePubKey() message to the address of account actor that called this method.
    //   - Send() message to the `BURNT_ACTOR` address with the `Value` included in the message
    //    to be burnt.
    Release()

    // SendCross can be called by any user in the subnet to send
    // an arbitrary cross-net message to any other subnet in
    // the hierarchy.
    //
    // - methodNum: 9
    // - allowed callers: any account
    // - impacted state:
    //  - If Bottom-up message: update `Checkpoint` to include in its `CrossMsgMeta` a
    //  `CrossMsgs` with this new release message and an updated `Value`.
    //  It also triggers an update of `CheckMsgsRegistry` with the updated `CrossMsgs`.
    //  - If top-down message: Append the message to the `TopDownMsgs` of the next child subnet
    //  in the path. Update of `CircSupply` for the subnet specified as parameter in the method.
    // - side-effect message triggered:
    //   - ResolvePubKey() message to the address of account actor that called this method.
    //   - If bottom-up message: Send() message to the `BURNT_ACTOR` address with the
    //  `Value` included in the message to be burnt.
    SendCross(msg CrossMsgParams)

    // ApplyMessage can only be called as an `ImplicitMessage` by
    // the `SystemActor` and is used to perform the execution of a
    // of cross-net messages in the subnet.
    //
    // This method is called when a cross-net message is found in a
    // validated block and needs to be executed.
    // - It determines the type of cross-net message
    // - It executes the message and trigger the corresponding state changes.
    // - And it updates the latest nonce applied for the type of message.
    //
    // - methodNum: 10
    // - allowed callers: system actor address (executed implicitly)
    // - impacted state:
    //   - If bottom-up message: Increment `AppliedBottomUpNonce` and update
    //     `TopDownMsgs` of the next child subnet in the path
    //     if the message need to be propagated further down.
    //   - If top-down message: Increment `AppliedBottomUpNonce` and update
    //     `TopDownMsgs` of the next child subnet in the path
    // - side-effect message triggered:
    //   - If message directed to current network: Send() the message being executed
    //   to the right address.
    //   - If top-down message: SubnetMint() to reward actor to mint new funds to
    //    be sent to the right address when executed.
    // - invariants:
    //   - A top-down message can only be executed if its nonce is `AppliedTopDownNonce+1`.
    //   - A bottom-up message can only be executed if its nonce is `AppliedBottomUpNonce ||
    //     AppliedBottomUpNonce+1`
    //    value
    ApplyMessage(msg CrossMsgParams)

    // InitAtomicExec can be called by users to initiate an
    // atomic execution with some other subnet.
    //
    // - methodNum: 11
    // - allowed callers: any account
    // - impacted state: Update `AtomicExecRegistry` with the new execution
    // - side-effect message triggered:
    InitAtomicExec(params AtomicExecParams)

    // SubmitAtomicExec has to be called by all participants in an
    // atomic execution to submit their results and trigger the
    // propagation of the output (or the abortion) of the execution
    // to the corresponding subnets.
    //
    // - methodNum: 12
    // - allowed callers: any account involved in the atomic execution
    // - impacted state: Update `AtomicExecRegistry` with the new
    //  output provided, and any required update to the `ExecState`.
    //  If the execution succeeds or is aborted a new message is
    //  appended to the `TopDownMsgs` of all the subnets involved.
    // - side-effect message triggered: none
    // - invariants:
    //   - All outputs should match and lead to the same CID for the
    //   execution to succeed and it shouldn't have been aborted.
    SubmitAtomicExec(submit SubmitExecParams)

    // ReportMisbehavior is used to report a misbehavior from one
    // of the child subnets of the current network. This function
    // can send additional messages to the
    // `CheckEquivocation` method of the correponding subnet actor
    // to perform checks over the proof of misbehavior.
    // If the proof succeeds, the collateral for the subnet is slashed.
    //
    // - methodNum: 13
    // - allowed callers: any account
    // - impacted state:
    // - side-effect message triggered:
    ReportMisbehavior(SubnetID, invalid []Block, valid []Block)

    // Save can be used by any user of the subnet to trigger the persistence
    // of the state of the subnet in any storage system (IPFS, Filecion, etc.).
    // This method returns the CID and URI to retrieve the snapshot. It also keeps
    // in the SCA state a map of all the available snapshot and the latest epoch they
    // persist.
    //
    // NOTE1: This method is WIP and the interface may suffer changes in
    // the future. Once FVM has native support for starting deals on-chain,
    // the actor should be able to handle the full end-to-end storage of the
    // snapshot.
    // NOTE2: We are considering the implementation of a protocol that performs
    // the storage of incremental snapshots.
    //
    // - methodNum: 13
    // - allowed callers: any account
    // - impacted state:
    // - side-effect message triggered:
    Save() (Cid, URI)
```

## Consensus Interface
Each subnet can run its own implementation of a consensus algorithm. In order for different consensus implementations to operate seamlessly with the Filecoin stack, we decouple the core methods of the current consensus in its own interface. In order for a consensus implementation to be usuable in a subnet, it needs to implement this interface.
> Consensus Interface
```go
type Consensus interface {
    // Performs a complete check of a proposed block to either
    // accept it or reject it.
    ValidateBlock(ctx context.Context, b *types.FullBlock) (err error)
    // Light check performed when a block is received through
    // the pubsub channel.
    ValidateBlockPubsub(ctx context.Context, self bool, msg *pubsub.Message) (pubsub.ValidationResult, string)

    // Used by mining processes to assemble and propose a new
    // signed block.
    CreateBlock(ctx context.Context, w api.Wallet, bt *api.BlockTemplate) (*types.FullBlock, error)
}
```
An example of a BFT-like consensus protocol being integrated in HC through this consensus interface can be found [here](https://github.com/filecoin-project/mir)

> TODO: Add a section describing how to integrate new consensus algorithms into HC.

## Lifecycle of a subnet
The following section presents an overview of the lifecycle of a subnet.

### Spawning and joining a subnet
Creating a new subnet instantiates a new independent state with all its subnet-specific requirements to operate independently. This includes, in particular: a new pubsub topic that peers use as the transport layer to exchange subnet-specific messages, a new mempool instance, a new instance of the Virtual Machine (VM), as well as any other additional module required by the consensus that the subnet is running (built-in actors, mining resources, etc.).

To spawn a new subnet, peers need to deploy a new `SubnetActor` that implements the core logic for the governance of the new subnet. The contract specifies the consensus protocol to be run by the subnet and the set of policies to be enforced for new members, leaving members, checkpointing, killing the subnet, etc. For a new subnet to interact with the rest of the hierarchy, it needs to be registered in the `SCA` of the parent chain. The `SCA` is a system actor that exposes the interface for subnets to interact with the hierarchical consensus protocol. This smart contract includes all the available functionalities related to subnets and their management. And, as `SA`s are user-defined and untrusted, it also enforces security requirements, fund management and the cryptoeconomics of hierarchical consensus.

For a subnet to be registered in the `SCA`, the actor needs to send a new message to the `Register()` function of the `SCA`. This transaction includes the amount of tokens the subnet wants to add as collateral in the parent chain to secure the child chain. The `SA` may implement custom policies that need to be fulfilled before registering the subnet and triggering `Register()` messages to the `SCA`, like for instance waiting for a minimum number of validators to join the network and put some collateral. The `SA` will also need to require that enough collateral is staked before registering to ensure that the message succeeds. For a subnet to be activated in HC, at least `CollateralThreshold` needs to be staked in the `SCA` to be in an `Active` state.

This collateral is frozen through the lifetime of the subnet and does not become part of its circulating supply. These funds are slashed when a valid complaint in the subnet is reported to the parent, or when a validator of the subnet leaves and release its collateral. If the subnet's collateral drops below `CollateralThreshold`, the subnet enters an `Inactive` state, and it can no longer interact with the rest of the hierarchy. To recover its `Active` state, users of the subnet need to put up additional collateral.

### Leaving and killing a subnet
Members of a subnet can leave the subnet at any point by sending a message to the subnet's `SA` in the parent chain. If the miner fulfils the requirements to leave the subnet defined in the subnet's `SA` when it was deployed, a message to the `SCA` is triggered by the `SA` to release the miner's collateral.  If a validator leaving the subnet brings the collateral of the subnet below `CollateralThreshold`, the subnet gets in an `Inactive` state, and it can no longer interact with the rest of the chains in the hierarchy or checkpoint to the top chain. To recover its `Active` state, any participant in the protocol (within or outside the subnet, user or validator) needs to put up additional collateral. An `Inactive` subnet can be killed by calling the `Kill()` method of the subnet actor that propagates the `Kill()` signal (if all the checks pass) to the SCA.

Validators in a subnet may choose to implicitly kill it by stopping the validation of blocks. The subnet may still be holding user funds or useful state. If miners leave the subnet and take the collateral below the `CollateralThreshold`, users no longer have a way to get their funds and state out of the subnet. To prevent this from happening, the `SCA` includes a `Save()` function that allows any participant in the subnet to persist the state. Users may choose to perform this snapshot with the latest state right before the subnet is killed, or perform periodic snapshots to keep track of the evolution of the state. Through this persisted state and the checkpoints committed by the subnet, users are able to provide proof of pending funds held in the subnet or of a specific part of the state that they want to be migrated back to the parent. `Save()` is also used to enforce the [Data availability](#Data-availability "Data availability") of a subnet's state.

## Naming
Every subnet is identified with a unique `SubnetID`. This ID is assigned deterministically and is inferred from the `SubnetID` of the parent and the address of the subnet actor in the parent responsible for governing the subnet. The rootnet in HC always has the same ID, `/root`. From there on, every subnet spawned from the root chain is identified through the address of their `SA`. Thus, if a new subnet is being registered from an actor with ID `f0100`, the subnet is assigned an ID `/root/f0100`. Actor IDs are unique through the lifetime of a network. Generating subnet IDs using the `SA` ID ensures that they are unique throughout the whole history of the system.

The assignment of IDs to subnets is recursive, so the same protocol is used as we move deeper into the hierarchy. A subnet represented by `SA` with address `f0200` spawned in `/root/f0100` is identified as `/root/f0100/f0200`. To create the subnet ID of any subnet, we just need to add the address of its subnet actor as a suffix to its parent's ID.

This naming convention allows to deterministically discover and interact with any subnet in the system. It also offers an implicit map of the hierarchy. Peers looking to interact with a subnet only need to know their `SubnetID` and publish  a message to the pubsub topic with the same name.

Peers participating in a subnet are subscribed to all subnet-specific topics and are able to pick up the message. Subnet-specific pubsub topics are named also deterministically by using the subnet's ID as a suffix to the topic. Thus, subnets spawn at least three different topics for their operation: the `/fil/msgs/<subnetID>` topics to broadcast mempool messages; the `/fil/blocks/<subnetID>` topic to distribute new blocks; and the `/fil/resolver/<subnetID>` topic where cross-net content resolution messages are exchanged. These topics for subnet `/root/f0100` are identified as `/fil/msgs/root/f0100`, `/fil/blocks/root/f0100`, `/fil/resolver/root/f0100`, respectively.

Peers can also poll the available child chains of a specific subnet by sending a query to the `SCA` requesting a list of its children. This allows any peer to traverse the full hierarchy and update their view of available subnets.

In the future, HC may implement an additional DNS-like actor in the system that allows the discovery of subnets using human-readable names, performing a translation between a domain name and the underlying ID of a subnet.

### SubnetID
A `SubnetID` is the unique identifier of a subnet. While its string representation resembles a directory path (see examples above), the following object is used for its byte and in-memory representation (its serialized representation is the CBOR marshalling of this object):
```go
type SubnetID struct {
    // string representation of the parent SubnetID
    Parent string
    // Address of the subnet actor governing the operation
    // of the subnet in the parent.
    // (it must be an ID --i.e f00-- address)
    Actor address.Address
}
```

`SubnetID` includes the following convenience methods to aid in the use of `SubnetID`s.
> SubnetID methods
```go
// Returns the parent of the current SubnetID
Parent() SubnetID
// Returns the address of the Subnet actor for the Subnet
Actor() address.Address
// Returns the string representation of the SubnetID
String() string
// Returns the serialized representation of the SubnetID
Bytes() []byte
// Returns the in-memory representation (struct) of the SubnetID
// from its string representation. It errors if the string
// representation is not a valid SubnetID.
FromString(string) (SubnetID, error)
// Returns the common parent of the current subnet and the one
// given as an argument.
CommonParent(other SubnetID) SubnetID
// Returns the next subnet down in the hierarchy in the path of the
// receiving SubnetID, starting from the prefix given as an argument.
// It errors if there is no such path leading down.
//
// Example:
// `/root/f0100/f0200`.Down(`/root`) = `/root/f0100`
Down(other SubnetID) (SubnetID, error)
// Returns the next subnet up in the hierarchy in the path of the
// receiving SubnetID, starting from the prefix given as an argument.
// It errors if there is no such path leading up.
//
// Example:
// `/root/f0100/f0200`.Up(`/root/f0100`) = `/root`
Up(other SubnetID) (SubnetID, error)
```

## Hierarchical Address
HC uses [Filecoin addresses](https://spec.filecoin.io/#section-appendix.address) for its operation. In order to deduplicate addresses from different subnets, HC introduces a new address protocol with ID `4` called _hierarchical address (HA)_. A hierarchical address is just a raw Filecoin address with additional information about the subnet ID the address refers to.

There are 2 ways a Filecoin address can be represented. An address appearing on chain will always be formatted as raw bytes. An address may also be encoded to a string; this encoding includes a checksum and network prefix. An address encoded as a string will never appear on chain, this format is used for sharing among humans. A hierarchical address has the same structure of a plain Filecoin address. In this case, the payload of hierarchical addresses don't have a fixed size, and their size depend on the length of the `SubnetID` and the raw address used. Thus, the payload of a hierarchical address has the following structure:
- __Subnet Size (1 byte)__: Represents the number of bytes of the `SubnetID` as a `varInt`. It is used to delimit the bytes of the payload of the `SubnetID` from those of the raw address. Due to the maximum size of `SubnetID` the `varInt` will never use more than 1 byte.
- __Address Size (1 byte)__: Represents the size of the raw address as a `varInt` (which is also expected to be at most 1-byte-long). HA supports all types of filecoin addresses as raw addresses (from IDs to BLS and SECPK addresses). The size of the address flags the total size of the hierarchical address payload. Consequently, the total size of a hierarchical address' payload can be easily computed as `2 + SIZE_SUBNETID + SIZE_ADDR`.
- __SubnetID (up to 74 bytes)__: String representation of the subnet ID (e.g. `/root/f01010`). The maximum size is set to support at most 3 levels of subnets using subnet IDs with the maximum id possible (which may never be the case, so effectively this container is able to support significantly more subnet levels). The size of `/root` is 5 bytes, and each new level can have at most size `23` (`22` bytes for the number of characters of the `MAX_UINT64` ID address and 1 byte per separator).
- __RawAddress (up to 66 bytes)__: Byte representation of the raw address. The maximum size is determined by the size of the SECPK address, the largest type of address in the Filecoin network.

Thus, the maximum length of the payload of a hierarchical address is set to 142 bytes. The string representation of HA addresses is encoded as every other Filecoin address (see [spec](https://spec.filecoin.io/#section-appendix.address.string)).

> Payload of Hierarchical Address
```
|----------|-------------------------------------------------------------------------------------------------------------------------------|
| protocol |                                                            payload                          |                                 |
|----------|-------------------------------------------------------------------------------------------------------------------------------|
|    4     | subnet size (1 byte) | raw_addr size (1 byte) | subnetID (up to 74 bytes) | separator (1 byte) | raw address (up to 66 bytes) |
|----------|-------------------------------------------------------------------------------------------------------------------------------|
```

With hierarchical addresses three new functions are introduced to Filecoin addresses:
- `Raw()`: Returns the raw address of the hierarchical address. If it is not an HA, it still returns the corresponding raw address.
- `Subnet()`: It returns the subnet ID of the HA. It returns an error or an `Subnet.Undef` if the address is not an HA.
- `Levels()`: Returns the number of levels in the `SubnetID` included in the HA address.
- `PrettyString()`: Returns a beautified version of an HA address like `/root/f0100:<raw address string>`. This is method is only available for HA. For the rest of addresses it just returns `String()`.

Finally, a pair of keys from a user control the same address in every subnet in the system. Thus, the raw address determines the ownership of a specific HA.

## Checkpointing
Checkpoints are used to anchor a subnet's security to that of its parent network, as well as to propagate information from a child chain to other subnets in the system. Checkpoints for a subnet can be verified at any point using the state of the subnet chain, which can then be used to generate proofs of misbehaviors in the subnet (or so-called _fraud/fault proofs_), which, in turn, can be used for penalizing misbehaving entities (_"slashing"_). See [detectable misbehaviors](#Detectable-misbehaviors "Detectable misbehaviors") for further details.

Checkpoints need to be signed by miners of a child chain and committed to the parent chain through their corresponding `SA`. The specific signature policy is defined in the `SA` and determines the type and minimum number of signatures required for a checkpoint to be accepted and validated by the `SA` for its propagation to the top chain. Different signature schemes may be used here, including multi-signatures or threshold signatures among subnet miners. For instance, in the reference implementation of `SA`, the actor waits for more than `2/3` of the validators in the subnet to send the valid checkpoint signed before propagating it to the `SCA` for commitment. Alternative verification policies for a subnet can be implemented in the `SubmitCheckpoint()` function of the subnet actor interface.

In order for a new checkpoint to be accepted for commitment in `SCA`, the source of the message `CommitChildCheckpoint()` needs to be the address of the subnet actor of the corresponding subnet; the subnet needs to be in an `Active` state (i.e. its collateral is over `CollateralThreshold`); the epoch of the checkpoint should be a multiple of the subnet's `CheckPeriod` and larger that that of the previous checkpoint; and the checkpoint must point to the `CID` of the previous checkpoint committed by the subnet.

When spawned, subnets are allowed to configure the `CheckPeriod` that better suits their needs and the specifics of their consensus algorithm.

### Checkpoint commitment
As an example, lets consider a checkpoint for subnet `/root/f0100/f0200`. Every `CheckPeriod` (in terms of subnet block time), validators access the checkpoint template that needs to be signed and populated by calling the `CheckpointTemplate()` state accessor from `SCA` in `/root/f0100/f0200`. Once signed and populated, checkpoints from `/root/f0100/f0200` are submitted to the `SA` with ID `f0200` of subnet `/root/f0100` by sending a message to `SubmitCheckpoint()`. After performing the corresponding checks and waiting for the commitment conditions (i.e. `+2/3` of the validators sending a signed checkpoint in its reference implementation), this actor then triggers a message to `/root/f0100` `SCA`'s `CommitChildCheckpoint()` function to commit the checkpoint.

When the checkpoint is committed, the `SCA` in `/root/f0100` is responsible for aggregating the checkpoint from `/root/f0100/f0200` with those of other children of `/root/f0100` and for generating a new checkpoint for `/root/f0100`, which is then propagated to its parent chain, `/root`. The commitment of checkpoints also triggers the execution and propagation of cross-net messages. As checkpoints flow up the chain, the `SCA` of each chain picks up these checkpoints and inspects them to propagate potential state changes triggered by messages included in the cross-net messages that have the `SCA`'s subnet as a destination subnet (see [Cross-net messages](#Cross-net-messages "Cross-net messages")).

Every checkpoint for a subnet points to the previous checkpoint being committed to ensure their integrity.

> Checkpoint template read-only function in SCA
```go
// Returns the checkpoint template to be populated for the current
// checkpoint window. The current checkpoint window is computed by
// (currEpoch / CheckPeriod) * CheckPeriod. This determines the checkpoint
// that needs to be populated and signed for the current window.
CheckpointTemplate() Checkpoint
```

As shown on the next figure, the checkpointing protocol has two distinct stages:
- __Checkpoint Window__: In this window, the `SCA` opens a checkpoint template and starts populating it with cross-net messages arriving to the subnet (and that need to be propagated further inside the checkpoint) and with the aggregated checkpoints committed from the current subnet's children. The checkpoint window for the checkpoint in epoch `n` starts at `n-CheckPeriod` and ends at epoch `n`.
- __Signing Window__: The signing window is the time range reserved for validators of the subnet to populate the checkpoint template with the corresponding proof of the state of the checkpoint, to sign the checkpoint, and to submit it to the corresponding `SA` in the parent for committment. The signing window for the checkpoint in epoch `n` goes from `n` to `n+CheckPeriod`. Consequently, the signing window for the checkpoint of epoch `n-CheckPeriod` and the checkpoint window for the checkpoint of epoch `n` are run in parallel. The checkpoint template provided by the `SCA` has `CrossMsgs`, `PrevCheck`, and `Epoch` already populated, and validators only have to add the corresponding `Proof` and sign it. If the SA is not able to gather enough votes for the commitment of the checkpoint in epoch `n`, or no checkpoint is committed in that epoch, the slot is missed, and the protocol advances to the next checkpoint window but in this case the template for `n+1` points to the last checkpoint committed, in our example `n-1`. Thus, if a checkpoint commitment fails for any reason the epoch is skipped and the template moves to the checkpoint window for the next epoch.


![](https://hackmd.io/_uploads/HkAodIuFc.png)


## Cross-net messages
Users in a subnet interact with other subnets through cross-net transactions (or messages). The propagation of a cross-net transaction may slightly differ depending on the location of subnets in the hierarchy (i.e. if moving up or down the hierarchy). In particular, we distinguish the following type of cross-net messages:

- __Top-down messages__ _(brown)_ are cross-net messages directed towards a subnet that is lower in the hierarchy (e.g. from `/root` to `/root/t02`).
- __Bottom-up  messages__ _(green)_ are cross-net messages directed towards a subnet that is higher in the hierarchy but shares the same prefix (e.g  from  `/root/t01` to `/root`).
- __Path messages__ _(pink)_. Every message routed in the hierarchy can be seen as a combination of top-down and bottom-up transactions. Path messages are cross-net messages in which the source and destination subnets are not in the same branch. These are propagated through bottom-up messages (i.e. `CrossMsgMeta` in checkpoints) up to the common parent (`/root`, in the worst case) and through top-down messages from there to the destination.

![](https://hackmd.io/_uploads/r1af_cd99.png)

New cross-net messages from a subnet are sent by sending a message to the `SendCross()`, `Fund()`, or `Release()` functions of the `SCA` of the corresponding subnet. `SendCross()` sends an arbitrary message specified as an argument to the subnet in `Destination`; while `Fund()` initiates a top-down message to a child subnet with an amount of native tokens to the source's address in the subnet; and `Release()` sends and amount of native tokens to the source's address in the parent. When any one of these messages is received, the `SCA` evaluates if it is a top-down or a bottom-up message and routes it correspondingly (by notifying the children or including the message in a checkpoint, respectively).

### Cross-net message pool
Nodes in subnets have two types of message pools: an internal pool to track unverified messages originating in and targeting the current subnet, and a `CrossMsgPool` that listens to unverified cross-msgs directed at (or traversing) the subnet. In order for cross-msgs to be verified and executed, they need to be run through the consensus algorithm of the subnet and included in a valid subnet block.

Full nodes in subnets are required to be full nodes of their parent in order to listen to events in their parent's `SCA` and their own subnet actor. The `CrossMsgPool` listents to the `SCA` and collects any new cross-net messages appearing at the `SCA`. Whenever the subnet's parent`SCA` receives a new top-down message or collects a new bottom-up `CrossMsgMeta` from a child checkpoint, the `CrossMsgPool` is conveniently notified. Top-down messages can be proposed to and applied directly in the subnet. For bottom-up messages, the cross-msg pool only has the CID of the `CrossMsgMeta` that points to the cross-msgs to be applied and, therefore, needs to make a request to the [Subnet Content Resolution Protocol](#Subnet-Content-Resolution-Protocol "Subnet Content Resolution Protocol") to retrieve the raw messages so they can be proposed and applied in the subnet.

Blocks in subnets include both messages originating within the subnet and cross-msgs targeting (or traversing) the subnet. Both types can be differentiated by looking at the `From` and `To` of the messages: cross-net messages include a `hierarchical address` (with subnet information) in both fields, while plain subnet messages include raw addresses in these fields. When a new block including top-down cross-msgs is verified in the subnet consensus, the cross-msgs are committed and every node receiving the new block executes the cross-msgs to trigger the corresponding state changes and fund exchanges in the subnet.

### Cross-net message execution
Cross-msgs in a block are implicitly executed by calling the `ApplyMsg()` of the subnet's `SCA` from the `SystemActor`. In the execution of a new block, the `TipSetExecutor` checks if the message to be applied is a plain subnet message or a cross-net message. If it is a cross-net message, the `TipSetExecutor` tailors a new message to the `SCA`, calling `ApplyMsg()` and including the cross-net message to be executed as a parameter. This new message is applied implicitly in the node with `ApplyImplicitMsg()` (see [how messages to the `CronActor` and rewards are executed](https://spec.filecoin.io/#section-systems.filecoin_vm.interpreter.implicit-messages) in the Filecoin spec).

What `ApplyMsg()` does to execute the cross-net message is:
- To check if it is a top-down or bottom-up message.
- According to its type, see if the message has the correct nonce according to the value of `AppliedTopDownNonce` and `AppliedBottomUpNonce`, respectively.
- Determine if the destination of the message is the current subnet or some other subnet in the hierarchy:
    - If the message is for the current subnet, the `From` and `To` of the cross-net message are translated into raw addresses, and a new `Send()` is called for the message in order to trigger the corresponding state changes in the subnet.
        - If the message is a top-down message, before the `Send()` of the cross-net messages, the amount of new tokens included in the `value` of the message (and that were locked in the `SCA` of the parent) need to be minted to allocate them to be used in the cross-net message. Thus, top-down messages mint new tokens in the subnet (with the consequent lock in the parent), while bottom-up messages burn native tokens in the subnet when they propagate bottom-up messages.
If the message's destination is not the current subnet, the destination `Subnet` is checked to determine if the message needs to be propagated as a top-down or a bottom-up message, conveniently adding it in `TopDownMsgs`of the next subnet in the messages path to the destination, or by including it in the next checkpoint, respectively.
- Increment the corresponding `AppliedNonces`.

### Top-down messages
When a new top-down cross-net message is sent to the `SCA` by calling `Fund()`, or `SendCross()` with a destination which is down in the hierarchy, the `SCA` of the source subnet:
- Checks which child is the next subnet in the path to the messages destination.
- Assigns to the message the subsequent `Nonce` to the latest one used for that subnet. Every time a new top-down message to the subnet arrives, the `SCA` increments a nonce that is unique for every cross-net message to that destination. These nonces determine the total order of arrival of cross-msgs to the subnet; without them, different consensus nodes could execute different orderings, leading to nondeterminism.
- Checks that the `From` and `To` of the message include `HA` addresses with the right subnets.
- Stores the message to notify its propagation in the `TopDownMsgs` of the corresponding child subnet.
- Locks in the `SCA` the number of native tokens included in the `value` of the message, increasing by the same amount the `CircSupply` of the subnet. These funds will be frozen until a bottom-up transaction releases them back to the parent. In this way, the `SCA` keeps track of the circulating supply of child subnets and is responsible for enforcing the firewall requirement in subnets (whenever native tokens want to be released from it, see [bottom-up messages](#bottom-up-messages)).

When a new cross-net message to a subnet is included in the `TopDownMsgs` in the parent subnet, the validators of the child subnet, who follow the parent consensus, are notified through their `CrossMsgPool` about this new top-down message. The `CrossMsgPool` waits for a `finalityThreshold` before proposing the message to be sure that the top-down message commitment can be considered final (this threshold may change according to the requirements of the subnet and the specific consensus algorithm used by the parent. The threshold for BFT-like consensus may be `1` or close to `1`, while sync consensus algorithms like PoW may require larger values). After the `finalityThreshold`, validators in the child subnet will check the latest `AppliedTopDownNonce` to fetch all unverified cross-net messages up to the latest one included in `TopDownMsgs` and propose them for their inclusion in a block and subsequent execution.

![](https://hackmd.io/_uploads/rynGK2ut5.png)


### Bottom-up messages

#### Including messages in `CrossMsgMeta`
Bottom-up messages are created by sending a message to the `Release()` or `SendCross()` methods of the source subnet's `SCA`. `Release()` sends a cross-net message to the parent of the subnet releasing some funds from the subnet, while `SendCross()` sends an arbitrary message and is routed as a bottom-up message when it includes in its `CrossMsgParams` a destination subnet in the upper layers of the hierarchy or with a common parent higher in the hierarchy. Bottom-up messages are propagated inside checkpoints. At every checkpoint period, the `SCA` collects and aggregates all `CrossMsgMeta` from bottom-up transactions originated in the subnet, as well as all the `CrossMsgMeta`. All these `CrossMsgMeta`are included in the next checkpoint for propagation up the hierarchy.

Whenever a new bottom-up message is triggered in a subnet, its `SCA`:
- Burns the amount of native tokens included in the `value` of the message in the subnet.
- Checks the checkpoint being populated in the current checkpoint window and checks if it already has a `CrossMsgMeta` with the same destination of the message.
    - If the `CrossMsgMeta` doesn't exist in the checkpoint, the `SCA` creates a new `CrossMsgs` appending the cross-net message in the `CrossMsgsRegistry` of the `SCA`, and includes in the checkpoint a new `CrossMsgMeta` for the destination including the `CID` of the `CrossMsgs` stored in the registry.
    - If the `CrossMsgMeta` for the destination exists in the checkpoint, the `SCA` gets from the `CrossMsgsRegistry` the current `CID` included in the `CrossMsgMeta`, and it appends the newly created cross-net message to `Msgs`. The `SCA` then updates with the new `CID` (after appending the message) to the `CrossMsgMeta` for the checkpoint, deletes the outdated `CrossMsgs` from the registry, and includes the updated one.
    - In these updates, the total amount of native tokens included in the messages of the `CrossMsgMeta` is also updated in the `Value` field.
- Finally, when the signing window for the checkpoint closes, the checkpoint is propagated including a link to the cross-net message in the `CrossMsgMeta` of the checkpoint.


#### Executing bottom-up messages
When a new checkpoint for a child subnet is committed in a network, the `SCA` checks if it includes any `CrossMsgMeta` before storing it in its state. If this is the case, it means that there are pending cross-msgs to be executed or propagated further in the hierarchy. For every `CrossMsgMeta` in the checkpoint, the `SCA`:
- Checks if the `Value` included in the `CrossMsgMeta` for the source subnet is below the total `CircSupply` of native tokens for the subnet. If the `Value > CircSupply`, `SCA` rejects the cross-msgs included in the `CrossMsgMeta` due to a violation of the firewall requirement. If `Value <= CircSupply` then the `CrossMsgMeta` is accepted, and `CircSupply` is decremented by `Value`.
- Checks if the destination of the `CrossMsgMeta` is the current subnet, a subnet higher up in the hierarchy, or a subnet that is lower in the hierarchy.
    - If the `CrossMsgMeta` points to the current subnet or to some other subnet down the current branch of the hierarchy in its `To`, the `CrossMsgMeta` is stored with the subsequent `BottomUpNonce` in `BottomUpMsgsMeta` to notify the `CrossMsgPool` that the cross-msgs inside the `CrossMsgMeta` need to be conveniently executed (or routed down) by implicitly executing a message to the `ApplyMsg` method of the `SCA`.
    - If the `CrossMsgsMeta` points to a subnet that needs to be routed up, `SCA` executes the same logic as when a new bottom-up cross-msg is created in the subnet, but appending the `CrossMsgsMeta` into the `Meta` field of `CrossMsgs`. The corresponding `CrossMsgsMeta` of the current checkpoint is created or updated to include this meta for it to be propagated further up in the next checkpoint. Thus, the `CID` of the new `CrossMsgMeta` for the parent includes a single `CID` that already aggregates a link to the `CrossMsgMeta` of the child with cross-net messages that need to go even upper in the hierarchy.

Validators' `CrossMsgPool`s also listen for new `BottomUpMsgsMeta` being included in their subnet SCA. When a new `CrossMsgsMeta` appears in `BottomUpMsgsMeta` (after the committment of a checkpoint), the `CrossMsgPool` checks if `CrossMsgsMeta.Nonce > AppliedBottomUpNonce` to see if it includes cross-msgs that haven't been executed yet. If this is the case, the `CrossMsgPool`:
- Gets all `CrossMsgsMeta` in `BottomUpMsgsMeta` with `Nonce > AppliedBottomUpNonce`.
- Gets `CrossMsgMeta.Cid` and makes a request to the subnet content resolution protocol to resolve the `CrossMsgs` behind that `CrossMsgMeta`. These requests are directed to the subnet in `Source` and they resolve the CID from the subnet's `CrossMsgsRegistry`.
    - If the resolved `CrossMsgs` only includes elements in the `Msgs` field, they can be directly proposed in the next block for their execution.
    - If this is not the case and `CrossMsgs` includes in its `Meta` field `CrossMsgMetas` from its children, then these `CrossMsgsMeta` need to be resolved recursively until all the `CrossMsgsMeta` have been successfully resolved to their underlying messages.
- Then, as it happened for top-down messages, once the `CrossMsgPool` has all the bottom-up messages to be applied, it waits for a `FinalityThreshold` (so as to be sure that the checkpoint commitment can be considered final), after which all resolved cross-messages are proposed for inclusion and subsequent execution.

![](https://hackmd.io/_uploads/Bkrzj2uF5.png)

### Path messages
Path messages are propagated and executed as a combination of bottom-up and top-down messages according the path they need to traverse in the hierarchy. Let's consider a message from `/root/f0100/f0200` to `/root/f0100/f0300`. This message is propagated as a set of bottom-up message up to the closest common parent (`/root/f0100` in our example). When the checkpoint including the cross-net message from `/root/f0100/f0200` arrives to `/root/f0100`, the `CrossMsgMeta` is resolved, and from there on, the message is propagated as a top-down message from the closest common parent to the destination (in this case, from `/root/f0100` to `/root/f0100/f0300`),

#### Errors propagating cross-net messages
If at any point the propagation or execution of a cross-msg fails (either because the message runs out of gas in-transit, because the message is invalid in the destination subnet, or because the `CrossMsgMeta.Cid` can't be resolved successfully), the message is discarded and an error is tracked for the cross-net message.

> TODO: Come up with error codes for message failures and how to propagate them to the source. Only the source will be notified.

### Minting and burning native tokens in subnets
Native tokens are injected into the circulating supply of a subnet by applying top-down messages. When executed, these messages lock the number of tokens included in the `value` of the message in the `SCA` of the parent and trigger the minting of new tokens in the subnet. To mint new tokens in the subnet, we include a new `SubnetMint` method with `methodNum=5` to the `RewardActor`. `SubnetMint` can only be called by the `SCA` in a subnet through `ApplyMsg()` method when executing a message. `SubnetMint` funds the `SCA` with enough minted native tokens to provide the destination address with its corresponding subnet tokens (see [sample implementation](https://github.com/adlrocha/builtin-actors/blob/9d3dd0b0638e9974de3059e81c588ec7338bab53/actors/reward/src/lib.rs#L237), `ExternalFunding` is renamed to `SubnetMint` in the []latest implementations](https://github.com/adlrocha/builtin-actors/issues/12)).

Validators in subnets are exclusively rewarded in native-tokens through message fees, so the balance of the `RewardActor` in subnets is only used to increase the circulating supply in a subnet by order of the `SCA`. For new native tokens to be minted in a subnet, the same amount of tokens need to have been locked in the `SCA` of the parent.

> Note: This change of the reward actor is not required for the `rootnet`. We can have a custom bundle with the modified `RewardActor` to be used exclusively for subnets.

On the other hand, bottom-up messages release funds from a subnet, thereby reducing its circulating supply. In this case, burning the funds from the subnet is straightforward. When the bottom-up messages are included in a checkpoint, the `SCA` triggers a message with the `value` amount of native-tokens to the `BurnActorAddress` of the subnet. Once the checkpoint is committed to the parent and the messages executed, the same amount of native tokens will be released from the parent's `SCA` and sent in a message to the destination addresses of the bottom-up messages.

### Cross-net routing gas price
Cross-net messages from a source subnet, `sn_src`, to some other subnet in the hierarchy,`sn_dest`, need to be provided with enough gas for the message to be executed and routed successfully by every subnet in the path `Path(sn_src, sn_dest)`. Cross-net messages within a subnet are treated like any other message, and their execution triggers some state change that costs a certain amount of gas in the subnet, `gas_cost_sn`. The main difference for cross-net messages is that this execution and state change may translate into the propagation of the message to the next subnet in the path. However, for a user to be able to provide the message with enough tokens to pay for the gas, it needs to have a sense of the cost of execution in each subnet in the path.

To improve the UX and make cross-net gas costs more predictable, each subnet publishes basic parameters of their gas model at spawning time:
- `gas_model_type` (if based on miner tipping, EIP1559-like, etc.)
- `curr_base_fee` (if any)

> TODO: A general gas model that can configurable by subnets is currently being designed. This model will determine the specific parameters available for users and applications to determine the right amount of gas that they need to provide cross-net messages.

With this information, the source of the cross-net message includes a `gas_fee_limit_array` of `gas_fee_limit` amounts that the message is willing to allocate to each subnet in the hop. Subnets in the path won't be able to charge over the specified `gas_fee_limit` assigned for them. When a cross-net reaches a subnet for which `gas_fee_limit` is insufficient, it fails and an error message is propagated back to the source, along with the unspent gas. Thus, the total amount of tokens to be provided to a cross-net message is `msg_exec_fee + routing_fee = msg.value + (msg.gas_price * msg.gas_limit) + sum(gas_fee_limit in gas_fee_limit_array)`.

If, after the execution of the cross-net message in the destination, there are pending fees that haven't been spent, they are deposited in the balance of the source address in the destination subnet.

> TODO: Tracking all the balance leftovers left behind in different subnets as a consequence of the execution of cross-net messages can be a nightmare for users and applications. It'd be great if we can come up with an efficient way to returns these leftovers to the address of the originator in the source subnet (i.e. the one that funded the message initially).

If a subnet wants to change the parameters of its gas model, it'll need to spawn a new subnet and migrate its traffic there. This prevents subnets from being able to manipulate their gas model and charge different gas costs from the ones publically advertised and harming message flow (e.g. forcing gas messages to run out of gas). Ideally, these public gas model parameters used to predict the total gas of a message as a cross-net message traverse a subnet can be extracted from the general crypto-econ model CEL is working on for the root network (and that will be extrapolated as a configurable general model for subnets).

## Subnet Content Resolution Protocol
For scalability reasons, when the destination subnet receives a new checkpoint with cross-net messages to be executed, it is only provided with the `CID` of the aggregated messages inside the `CrossMsgMeta`. For the subnet to be able to trigger the corresponding state changes for all the messages, it needs to fetch the payload of messages behind that `CID`, as illustrated in previous sections. The subnet `SCA` where the bottom-up message is generated keeps a `CrossMsgsRegistry` with `CID`s for all `CrossMsgsMeta` propagated (i.e. a content-addressable key-value store). This registry is used to fulfill content resolution requests.

Every subnet runs a specific pubsub topic dedicated to exchange Subnet Content Resolution messages. This topic always has the following ID: `/fil/resolver/<subnet_ID>`. So when a subnet receives a `CrossMsgMeta`, it only needs to tailor a query to the topic of the source subnet of the `CrossMsgMeta` for the `CID` of the messages included in it to resolve the messages.

The subnet content resolution protocol can be extended to resolve arbitrary content from the state of a subnet. Currently, the protocol includes handlers for the resolution by `CID` of the following objects.
- `CrossMsgs`: Set of messages being propagated in a checkpoint from a subnet and included in a checkpoint through a `CrossMsgMeta`.
- `LockedStates`: The input state locked for an atomic execution (see [Atomic Execution Protocol](#Atomic-Execution-Protocol "Atomic Execution Protocol"))
- `Checkpoints`: Committed checkpoints of a subnet in the parent `SCA`

> TODO: Due to how the MVP was implemented, the content resolution protocol includes a large amount of message types (one per object resolution). This can be simplified and is expected to be done before moving the protocol into production. See the [following issue](https://github.com/filecoin-project/eudico/issues/146) for further details. The spec will be updated once this is implemented.

### Resolution approaches
The protocol implements two approaches to resolve content:

- A __push__ approach, where, as the checkpoints and `CrossMsgMetas` move up the hierarchy, miners publish to the pubsub topic of the corresponding subnet the whole tree of `CrossMsgs` behind the `CrossMsgsMeta` `CID`, which includes all the messages targeting that subnet from a specific source. To push the message, the content resolution manager publishes a `Push` message in the resolver topic of the destination subnets specifying the type of content being pushed along with its CID. When new checkpoints are committed, source subnet's proactively push the content to the destination subnets for which `CrossMsgsMeta` have been included in the checkpoint. When validators and full nodes in the subnet come across these `Push` messages, they may choose to pick them up and cache/store them locally for when the checkpoint with the `CrossMsgsMeta` directed to them arrives, or discard them (in which case, they will need to explicitly resolve the content when required).

- A __pull__ approach, where, upon a destination subnet receiving a checkpoint with cross-net messages directed to it, miners' `CrossMsgsPool`s publish a `Pull` message in the source subnet's pubsub topic to resolve the cross-net messages for the specific `CID`s found in the tree of cross-net message meta. These requests are answered by publishing a new  resolve message in the requesting subnet with the corresponding content resolution. The source subnet answers to the resolver topic of the subnet originating the request with a `ResponseMeta` message including the resolution of the `CID`. This new broadcast of a content resolution to the subnet's pubsub channels gives every cross-net message pool a new opportunity to store or cache the content behind a `CID` even if they do not yet need it.

- A __peer-to-peer fallback__: These push and pull protocols operate through the broadcast of messages to the resolver topics of the corresponding subnets, but what if the propagation of these messages fails? As a last-resort fallback, HC peers include a peer-to-peer protocol to allow the direct request of `CrossMsgMeta` and other subnet-related information. Peers can choose to directly request the resolution of content from peers they know are participating in the subnet holding the content. Peers can use the validators of a subnet as their endpoints for these requests as their `multiaddress` is published on-chain. Additionally, other peers (and external storage services) may advertize themselves as _"servers"_ of content for a subnet (see [data availability](#data-availability) for further details).
> Note: This fallback protocol is not implemented yet as part of the MVP.

All these approaches to content resolution include safe-guards to prevent DoS attacks.
- Messages that are equal to another message recently exchanged in the topic (independently of their source) are immediately rejected.
- Malformed messages are immediately rejected.
- Peers sending requests for non-existing `CID`s for a subnet are penalized.
- All `Response` and `Push` messages are self-certified. Peers sending content that doesn't correspond to the `CID` included in the message are penalized.

> Content Resolution Message Types
```go
type MsgType enum (
    // PushMeta content to other subnet
    PushMeta MsgType = iota
    // PullMeta requests CrossMsgs behind a CID
    PullMeta
    // ResponseMeta is used to answer to pull requests for cross-net messages.
    ResponseMeta
    // PullLocked requests for locked state needed to perform atomic exec.
    PullLocked
    // ResponseLocked is used to answer to pull requests for locked state.
    ResponseLocked
    // PullCheck requests the checkpoint for subnet. This request
    // needs to be sent to the parent of a subnet (which is the one)
    // persisting the committed checkpoints for subnets.
    PullCheck
    // ResponseCheck answers a request for a checkpoint pull request.
    ResponseCheck
)
```

> Resolve message data structure
```go
type ResolveMsg struct {
	// From subnet
	From SubnetID
	// Message type being propagated
	Type MsgType
	// Cid of the content
	Cid Cid<Type>
	// MsgMeta being propagated (if any)
	CrossMsgs CrossMsgs
	// Checkpoint being propagated (if any)
	Checkpoint Checkpoint
	// LockedState being propagated (if any).
	Locked atomic.LockedState
    // address wrapped as string to support undef serialization
	Actor  string
}
```

![](https://hackmd.io/_uploads/rJd0_6tK9.png)

### Data availability
Peers requesting content from another subnet trust that participants in the other subnet, from which a checkpoint with cross-messages has been propagated, will answer content resolution requests sent to the subnet. Intuitively, the node that triggered the cross-message has no incentive to deny access to this data (as his funds have already been burnt), but data availability is an issue that is nevertheless worth addressing. The aforementioned design of the content resolution protocol assumes at least _one honest participant in the subnet_ (i.e. a peer that always answers content resolution requests successfully) _and that the data in the subnet is always available_. In a real environment, these assumptions may not hold and more complex schemes may be needed to incentivize subnet peers and ensure that every content resolution request between subnets is fulfilled and, consequently, a high level of data availability.

To overcome this issue, `SCA` in subnets include the `Save()` function and peers implement a protocol to backup the state of the function in any storage system where data can be retrievable and available independently of the state of a subnet (let this be Filecoin storage, IPFS, or any other decentralized or centralized storage systems). Having the state available is key for:
- The execution and validations of cross-net messages.
- Creating fraud/fault proofs from detectable misbehaviors in a subnet.
- Migrating the state of a subnet and spawning a new subnet from the existing state of another network.

> TODO: For this purpose, a `Persistence` interface will be explored and implemented in future iterations of the protocol. Ideally we should piggy-back from all the available storage in the Filecoin network, FVM native integration with storage primitives, and all the data retrievability work being done by [CryptoNetLab](https://research.protocol.ai/groups/cryptonetlab/) or [Filecoin Saturn](https://github.com/filecoin-project/saturn-node).

## Atomic Execution Protocol
An issue arises when state changes need to be atomic and impact the state of different subnets. A simple example of this is the atomic swap of two assets hosted in different subnets. The state change in the subnets needs to be atomic and it requires from state that lives in both subnets. To handle these atomic transactions, the parties involved in the execution can choose any subnet in the hierarchy in which they both have a certain level of trust to migrate the corresponding state and orchestrate the execution. Generally, subnets will choose the closest common parent as the execution subnet, as they are already propagating their checkpoints to it and therefore leveraging shared trust.

A cross-net atomic execution takes tuples of input states and returns tuples of outputs states, which may belong to different subnets, but should appear as a single transaction in which all input/output states belong to the same subnet. The atomic execution protocol has the following properties:

- __Timeliness__: The protocol eventually completes by committing or aborting.
- __Atomicity__: If all involved subnets commit and no subnet aborts beforehand, the protocol commits and all subnets involved have the output state available as part of their subnet state.
  Otherwise, the protocol aborts and all subnets revert to their initial state.
- __Unforgeability__: No entity in the system (user or actor) is able to forge the inputs and outputs provided for the execution or the set of messages orchestrating the protocol.

Finally, the data structures used by the protocol need to ensure the __consistency__ of the state in each subnet (i.e. that the output state of the atomic execution can be applied onto the original state --- and history --- of the subnet without conflicts). That being said, it is worth noting that the _firewall requirement_ limits against the impact of an attack involving native token exchanges but can't protect against an attack over the state of a subnet (including non-native tokens). To cover against this kind of attack, collateral is used (see [detectable misbehaviors](#Detectable-misbehaviors "Detectable misbehaviors")).

#### Atomic execution primitives
High-level, the atomic execution protocol involves:
- A set of users `[U_s1, ..., U_sn]` from `n` different subnets (`S1, ..., Sn`).
- A set of partial states (or `LockableState`) from the actors involved in the atomic execution of these subnets: (`PS_s1, ..., PS_sn`).
- A `merge(a: LockableState, b: LockableState) -> LockableState` function that recombines two partial states from a subnet into a common consistent one.
- An `exec(msg: Msg[], S: LockableState) -> OutputState` that computes an output state after executing the list of messages against the combination of the input partial states.
- A `finalize(ps: LockableState, o: OutputState)` where participants update their respective partial states in their subnets with the output state committed by all parties.

Actors that looking to support atomic executions of their functions need to implement a set of interface and basic primitives for their operation.
- The `LockableActor` interface provides a set of basic functions every to interact with `LockableState` in the actor. The `LockableState` are the different objects in the state that can be locked and used to perform atomic executions in the actor.
> LockableActor interface
```go
// LockableActor defines the interface that needs to be implemented by actors
// that want to support the atomic execution of some (or all) of their functions.
type LockableActor interface {
    // Inherits from the core interface for VM actors
    runtime.VMActor
    // Lock defines how to lock the state in the actor.
    // (methodNum = 2)
    Lock(rt runtime.Runtime, params *LockParams) Cid<LockedState>
    // Merge takes external locked state and merges it to
    // the current actors state.
    // (methodNum = 3)
    Merge(rt runtime.Runtime, params *MergeParams)
    // Finalize merges the output of an execution and unlocks the state.
    // (methodNum = 4)
    Finalize(rt runtime.Runtime, params *UnlockParams)
    // Abort unlocks the state and aborts the atomic execution.
    // (methodNum = 5)
    Abort(rt runtime.Runtime, params *LockParams)
    // StateInstance returns an instance of the lockable actor state
    StateInstance() LockableActorState
}
```
- The state of the actor needs to implement the `LockableActorState` interface that determines how to access persisted state from locked states and outputs from an execution. Actors supporting atomic executions are required to persist and make locked states retrievable for the operation of the protocol. In the reference implementation of the protocol, `LockableActor`s include a `LockedMapCID` HAMT that persists the locked state of all ongoing atomic executions where the key is the `CID`, which uniquely identifies the locked state, and the value is the `LockedState`. Of course, the actor state needs to be CBOR-deserializable.
> LockableActorState interface
```go
type LockableActorState interface {
	cbg.CBORUnmarshaler
	// LockedMapCid returns the cid of the root for the locked map
	LockedMapCid() Cid<HAMT<Cid, LockedState>>
	// Output returns locked output from the state.
	Output(*LockParams) *LockedState
}
```
- Any object of the state that needs to be lockable has to implement the `LockableState` interface. The object needs to be CBOR-serializable (like any other actor state) and it needs to implement the desired merging logic (the contract-specific strategy used to merge distinct states of an object).
> `LockableState`interface.
```go
// LockableState defines the interface required for states
// that needs to be lockable.
type LockableState interface {
    Marshalable
    // Merge implements the merging strategy for LockableState according
    // when merging locked state from other subnets and the output
    // (we may want to implement different strategies)
    Merge(other LockableState, output bool) error
}
```
- The representation of `LockedState` objects is done by wrapping the serialized data with a lock. `LockedState` includes a set of convenient functions to interact with the data.

> Note: The current MVP of the atomic execution protocol hasn't been ported to target the FVM yet. These abstractions may end up being improved and more elegant after the port (macros will be included to infer a lot of the boilerplate code required to implement actors that support atomic executions).

> `LockedState` object
```go
// LockedState includes a lock in some state.
type LockedState struct {
    Lock bool
    S    []byte
}

///////////////////////////
/// Methods of LockedState
///////////////////////////
// Returns the CID for the locked state
Cid() Cid<LockedState>
// Sets the state for a lockedState object container
SetState(ls LockableState) error
// Locks the state
LockState() error
// Unlock the state
UnlockState() error
// Check if locked
IsLocked() bool
// Wraps LockableState into a `LockedState` object
WrapLockableState(s LockableState) (*LockedState, error)
// Unwep the `LockableState` inside the `LockedState`
UnwrapLockableState(s *LockedState, out LockableState) error
```

- Finally, to signal the specific methods and parameters for which the atomic execution protocol is being performed, message params for `LockableActor`s have the following structure.
> Params of atomic execution methods
```go
// LockParams wraps serialized params from a message with the requested methodnum.
type LockParams struct {
    Method MethodNum
    Params []byte
}

// UnlockParams identifies the input params of a message
// along with the output state to merge.
type UnlockParams struct {
    Params *LockParams
    State  []byte
}

// MergeParams wraps locked state to merge in params.
type MergeParams struct {
    State []byte
}
```

#### Implementation of the protocol
The atomic execution protocol consists of the following phases, which, combined, resemble a two-phase commit protocol with the `SCA` of the least common ancestor/parent serving as a coordinator:

- __Initialization__: To signal the start of an atomic execution, the parties involved interact off-chain to agree on the specific execution they want to perform and the input state it will involve.
    - To start the execution, each party needs to lock, in their subnet, the state that will be used as input for the execution. This is done by sending a message to the `Lock()` function of the `LockableActor` involved in the execution, indicating in the `LockParams` the `MethodNum` and `Params` the parties agreed on for the atomic execution. `Lock()` returns the `CID` of the locked state and persists it in the corresponding `LockedStateRegistry` of the actor. Locking the state prevents new messages from affecting the state and leading to inconsistencies when the output state is migrated back. From now on, the actor won't accept any message involving the locked state. The locking of the input state in each subnet signals the beginning of the atomic execution.
    - One of the parties needs to initialize the execution by sending an `InitAtomicExec` message to the `SCA` of the parent responsible for orchestrating the execution specifying the `AtomicExecParams` (i.e. the list of messages and a map with the HA address and the `CID` of the input state for all the parties involved). If the initiator already has performed the off-chain execution (see next bullet), it can also submit the CID of its output state as part of the initialization message.
    - In its current implementation, the `SCA` verifies that it is the common parent of all parties that accepted the execution. To uniquely identify the atomic execution, it computes the `CID` of the `AtomicExecParams`. This `CID` identifies the atomic execution in the `SCA` throughout its life. If the `InitAtomicExec` message succeeds, a new atomic execution is spawned for that CID in an `ExecInitialized` state.
> Note: At this point there's no deduplication of atomic executions in the same `SCA`. An atomic execution with the same `AtomicExecParams` can't be run twice in the same `SCA`. This is a limitation of the MVP implementation and it will be fixed in the next iteration by adding a nonce (see [issue](https://github.com/filecoin-project/eudico/issues/147)).

- __Off-chain execution__: Each party only holds part of the state required for the execution. In order for the parties in the execution to be able to execute locally, they need to request the state locked in the other subnet.
    - The `CID` of the input state is shared between the different parties in the execution during the initialization stage, and is leveraged by each party to request from the other subnets the locked input states involved in the execution.
    - On receiving the `CID` from the involved parties, peers can perform a request to the content resolution protocol for the `CID` of the input state in their source subnets by sending a `PullLocked` message.
    - Once every input state is received for all the `CID`s of the input state involved in the execution, each party runs the execution off-chain to compute the output state. This execution is performed by creating a temporal view of the state of the contract and merging the locked state from the other subnets. With the state ready, all messages of the atomic execution are implicitly applied ([see code](https://github.com/filecoin-project/eudico/blob/bb52565105f7fe716463b1e09dad7492569089f5/chain/consensus/hierarchical/atomic/exec/exec.go#L32) for further details).
    - The `OutputState` for the execution is then returned for commitment in the common parent.

- __Commit atomic execution in parent subnet__: As the parties involved perform the off-chain execution of `OutputState`, they commit it in the `SCA` of the parent subnet.
    - The commitment is performed by sending a message to the `SubmitAtomicExec` of the `SCA` in the common parent using `SubmitExecParams` as an input. In `SubmitExecParams` users need to include their `LockedState` for the `OutputState` after the execution and the `CID` of the atomic execution they are submitting.
    - The `SCA` checks that the `CID` of the `LockedState` matches the one submitted by the other parties and accepts the submission. The execution will stay in an `ExecInitialized` state until all the parties submit the right `LockedState` as an `OutputState`. When this happens, the execution is marked as `ExecSuccess` and the `SCA` triggers a top-down message to the corresponding subnet to the `Merge` function of the `LockableActor` involved in the execution on every subnet. This will trigger the merging of the `OutputState` and the unlocking of the locked state.
    -  To prevent the protocol from blocking if one of the parties disappears halfway or is malicious, any party is allowed to abort the execution at any time by sending a `SubmitAtomicExec` message to the corresponding `SCA` setting the `Abort` field of `SubmitExecParams` to true. This moves the execution to an `ExecAbort` state in the `SCA` and triggers a new top-down message to the `Finalize()` function of the `LockableState` involved in the execution on every subnet. These messages unlock the input state in the source subnets without merging any `OutputState` for the atomic execution.

- __Termination__  When the `SCA` receives the commitment of all the computed output states and if they all match, the execution is marked as successful, possible aborts are no longer taken into account, and subnets are notified, through a top-down message, that it is safe to incorporate the output state and unlock the input state (see details above). If, instead, the `SCA` receives an `ABORT` signal from some subnet before getting commitment from all subnets, it will mark the transaction as `ExecAborted` and each subnet is notified (through a cross-net message) that it may revert/unlock their input state without performing changes to the local state.

> Note: One open question when moving from fungible assets to general state is whether the firewall property can still hold. This generalized case is problematic since compromised subnets can send seemingly valid but actually corrupt input states to the other subnets involved in the atomic execution. Because subnets are only light clients of other subnets and rely on the security of their consensus, this can be hard to detect without an honest peer in the subnet raising the alert. As part of future work, we are exploring schemes that would allow the detection of invalid states in the protocol (see [detectabe misbehaviors](#detectable-misbehaviors)).

![](https://hackmd.io/_uploads/ryr_shptq.png)

> Atomic Execution Protocol data structures
```go
// AtomicExec is the data structure held by SCA for
// atomic executions.
type AtomicExec struct {
	Params    AtomicExecParams
	Submitted map[string]OutputCid
	Status    ExecStatus
}

type SubmitExecParams struct {
	Cid    Cid<LockedState>
	Abort  bool
	Output atomic.LockedState
}

type SubmitOutput struct {
	Status ExecStatus
}

// AtomicExecParams determines the conditions (input, msgs) for the atomic
// execution.
//
// Parties involved in the protocol use this information to perform their
// off-chain execution stage.
type AtomicExecParams struct {
	Msgs   []types.Message
	Inputs map[Cid]LockedState
}
```

## Collateral and slashing
> WIP. This is just a placeholder for this section. The content included is not final. Follow all design updates [here](https://hackmd.io/HpxNIaacTn2_t6jaDs9RcQ)

When validators join a subnet, they need to provide enough collateral for the subnet to cross the `CollateralThreshold` required to activate the subnet and to have validating rights of their own. The amount of collateral required needs to be enough to make misbehaviors economically irrational for subnet validators. Collateral works as follows:
- When a subnet is spawned, subnet founders determine the `gasRate` they want to initially support in their subnet. This parameter determines the "load" the child subnet expects to impose on the parent, and according to it, the parent sets the `CollateralThreshold` for the subnet. The collateral is also a metric of the subnet validators' _"skin in the game"_. Subnet validators are allowed to add more collateral than the `CollateralThreshold` to signal to users their "trustworthiness". However, the only requirement imposed by HC for a subnet to be `Active` (i.e. with the ability to commit checkpoints and interact with the rest of the network) is for the collateral to be over that threshold.
- Through the operation of the subnet, the `CollateralThreshold` may change according to the `CurrGasRate` reported by the subnet to the parent (through the commitment of checkpoints) and the `MisbehaviorsLevels`, a measure of the number of successful fault proofs for the child subnet committed in the parent, requiring validators to update their collateral accordingly.

### Detectable misbehaviors
In the following table, we specify a list of detectable misbehaviors that we envision users will be able to report through the commitment of fault proofs, along with the `impact` of the attack. This `impact` parameter is used to determine the amount of collateral slashed due to the reported misbehavior.

| Misbehavior         | Impact     | Description | Fault Proof |
|--------------|-----------|------------|------------|
| (R4.1) Agreement equivocation               |1|  Deviation on consensus (votes on consensus, checks PoS-based, etc.) | Block checks |
| (R4.2) Invalid state transition             |2| Consensus reaches valid blocks with an invalid state transition   | State replay  |

- __Agreement equivocation__: A malicious majority in a subnet can deviate from the consensus algorithm and propagate a block that should have been considered invalid if the protocol had been followed successfully. Agreement equivocations may arise, for instance, in blocks that do not pass all block checks (e.g. blocks are not mined in a different epoch, the block does not include the right ticket, or the block is not signed by the right leader); if the block doesn't include the right votes in a BFT-like consensus; etc.
To report an agreement equivocation, users need to submit to the parent's SCA the chain of blocks that includes the equivocated block and the valid chain that replaces the invalid block with a valid one. The SCA performs syntactic checks over the inputs and runs the `equivocation_check` function in the corresponding actor of the subnet actor to perform deeper consensus-specific checks. If any of these checks fail, the collateral of the subnet is slashed. The function `equivocation_check` is a mandatory function in the subnet actor interface, and it implements all the consensus-specific checks required to detect agreement equivocations.
Thus, if an agreement equivocation is detected in epoch `n`, a user looking to report the misbehavior needs to report the chain of the latest `n-finality`, including the equivocated block and the valid chain of `n-finality` blocks to the parent SCA. For BFT-like protocols, it may suffice to report the latest block where the equivocation arises, while for sync protocols like Nakamoto consensus -- without a clear metric of finality and where long-lasting forks may appear -- reporting agreement equivocations may be impossible.

> Note: The use of [Lurk](https://github.com/lurk-lang) proofs as native primitives in subnets' consensus can simplify and generalize the reporting and detection of agreement equivocations (to the extent of, potentially, completely removing them).

- __Invalid state transition__: Any malicious majority of a subnet can also push invalid state transitions in a valid block. Malicious validators can include messages in a valid block that trigger unallowed state changes. Invalid state transitions are a general misbehavior that may impact HC-specific processes like the commitment of checkpoints or the result of atomic executions.
In order to report an invalid state transition in a subnet, users need to submit to the parent SCA the chain of blocks from the closest valid committed checkpoint to the block where the invalid state transition happens. The parent SCA replays every state change in the reported chain and verifies that, indeed, an invalid state transition happened in the reported block. If the misbehavior is reported successfully, the collateral for the subnet is correspondingly slashed.
Thus, if an invalid state transition happens at block `n`, and the latest committed checkpoint was at block `n-x`, a user looking to report the misbheavior needes to submit to the SCA of the parent the chain of `x` blocks from `n-x` to `n` so the state can be replayed and the invalid state transition checked.
>Note: Along with the checkpoint at `n-x` a snapshot of the state at `n-x` may also need to be provided to enable the whole state of the subnet (for every contract) to be replayed.
