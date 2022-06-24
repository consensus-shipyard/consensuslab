Hierarchical Consensus Spec and FIPs
===
###### tags: `HC`, `ConsensusLab`, `Projects`, `Hierarchical Consensus`, `Spec`

> This document includes the latest version of the hierarchical conesnsus spec along with the relevant FIPs to be proposed to the Filecoin community.
 
## Revisions
- `2022-06-14`: Basic structure and WIP
- `2022-06-17`: Draft for up to cross-net messages.
- `2022-06-20`: Content resolution and atomic execution protocols. Detectable misbehaviors.
- `2022-06-21`: First draft with all sections and linking [FIP draft](https://hackmd.io/gBmBo6ChQ4ajqN8RtKdJ9A).

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
[Cross-message pool](#Cross-message-pool "Cross-message pool") | Reliable | No | |__FIP__ |
[Cross-message execution](#Cross-message-execution "Cross-message execution") | Reliable | No | |__FIP__ |
[Minting and Burning native tokens](#Minting-and-burning-native-tokens-in-subnets) | Reliable | No | | __FIP__ |
[Top-down messages](#Top-down-messages "Top-down messages") | Reliable | No | |__FIP__ |
[Bottom-up messages](#Bottom-up-messages "Bottom-up messages") | Reliable | No | |__FIP__ |
[Path messages](#Path-messages "Path messages") | Reliable | No | |__FIP__|
[Subnet Content Resolution Protocol](#Subnet-Content-Resolution-Protocol "Subnet Content Resolution Protocol") | Reliable | No | |__FIP__ |
[Resolution approaches](#Resolution-approaches "Resolution approaches") | Reliable | No | |__FIP__ |
[Data availability](#Data-availability "Data availability") | WIP/Draft |  | |N/A |
[Atomic Execution Protocol](#Atomic-Execution-Protocol "Atomic Execution Protocol") | Reliable | No | |__FIP__|
[Collateral and slashing](#Collateral-and-slashing "Collateral and slashing") | WIP/Draft |  | |N/A |
[Detectable misbehaviors](#Detectable-misbehaviors "Detectable misbehaviors") | WIP/Draft |   | |N/A |
[Cross-net routing gas price](#Cross-net-routing-gas-price "Cross-net routing gas price") | WIP/Draft |   | |N/A |

## Introduction
At a high level, hierarchical consensus (HC) allows for incremental, on-demand blockchain scaling and simplifies the deployment of new use cases with clearly isolated security domains that provide flexibility for varied use cases.

Consensus, or establishing total order across transactions, poses a major scalability bottleneck in blockchain networks. This is particularly the case when all validators are required to process all transactions. Regardless of the specific consensus protocol implementation used, this makes blockchains unable to increase their performance by adding more participants (scale-out).

In traditional distributed computing, one possible approach to overcoming this limitation is to resort to the partitioning, or sharding, of state processing and transaction ordering. In a sharded system the blockchain stack is divided into different groups called shards, each operated by its own set of nodes, which keep a subset of the state and are responsible for processing a part of the transactions sent to the system. 

The main challenge with applying traditional sharding to the Byzantine fault-tolerant context of the blockchain lies in the security/performance tradeoff. As miners are assigned to shards, there is a danger of diluting security when compared to the original single-chain (single-shard) solution. In both proof-of-work and proof-of-stake (PoS) blockchains, sharding may give the attacker the ability to compromise a single shard with only a  fraction of the mining power, potentially compromising the system as a whole. Such attacks are often referred to as _1\% attacks_. To circumvent them, sharding systems need to periodically reassign miners to shards in an unpredictable way, so as to cope with a semi-dynamic adversary. We believe that this traditional approach to scaling, which considers the system as a monolith, is not suitable for decentralized blockchains due to their complexity.  <!--and the fact that sharded systems reshuffle state without the consent of its owners, disrupting use cases that benefit from finer control over the system topology.-->

With __[Hierarchical Consensus](https://research.protocol.ai/publications/hierarchical-consensus-a-horizontal-scaling-framework-for-blockchains/)__ we depart from the traditional sharding approach and instead of algorithmically assigning node membership and load balancing the distribution of the state, we follow an approach where users and miners are grouped into subnets in which they can freely partake. Users (i.e. network participants) can spawn new independent networks, or child subnets, from the one they are operating in. __Each subnet can run its own independent consensus algorithm and set its own security and performance guarantees.__ Subnets in the system are organized hierarchically: each has one parent subnet and any number of child subnets, except for the root subnet (called _root network_ or _rootnet_), which has no parent and is the initial anchor of trust. To mitigate the 1\% attacks pertinent to traditional sharding, subnets in hierarchical consensus are [firewalled](https://ieeexplore.ieee.org/abstract/document/8835275), in the sense that a security violation in a given subnet is limited, in effect, to that particular subnet and its children, with bounded economic impact on its ancestors. This bounded impact of an attack is, at most, the circulating supply of the parent token in the child subnet. Moreover, ancestor subnets help secure their descendant subnets through _checkpointing_, which helps alleviate attacks on a child subnet, such as long-range and related attacks in the case of a PoS-based subnet.

Finally, subnets can semlessly communicate and interact with state hosted in other subnets through cross-net messages.

### Glossary
For clarity, we include here a glossary of HC-related concepts used throughout the spec:
- __Subnet__: Hierarchical consensus sidechain that keeps its own independent state, consensus algorithm, message pool, and broadcast layer, but that is able to seamlessly interact and communciate with other subnets in the hierarchy.
- __Rootnet__: First network from which all new subnets are spawned and the hierarchy is built. In our case, the Filecoin mainnet.
- __Parent Subnet__: Network from which a new subnet (child) is spawned. The parent is responsible for hosting the correponding subnet actors for their children.
- __Peer/Node of a subnet__: A full-node participating in a specific subnet (i.e. a member of the subnet syncing its full state).
- __User/Client__: Light-node of a subnet (i.e. participant not necessarily syncing the full state of the subnet).
- __Native Token__: Token of the rootnet used for the interaction with the HC protocol. In our case, `FIL`.
- __Circulating Supply__: Amount of native tokens injected for their use in a subnet.
- __Cross-net messages__: Messages originated in a subnet and directed to some other subnet in the hierarchy.
- __Collateral__: Amount of native tokens staked in a subnet's parent by subnet's validators. This stake is slashed when a misbehavior in the subnet is detected and successfully reported to the parent.

## Architecture
The system starts with a _rootnet_ which, at first, keeps the entire state and processes all the transaction in the system (like present-day Filecoin). Any subset of users of the rootnet can spawn a new subnet from it.

> High-level architecture of hierarchical consensus
![](https://hackmd.io/_uploads/BJVIhk8Fc.png)

This subnet instantiates a new network with its own state, independent from the root network, replicated among the subset of participants of the overall system who are members of the subnet. From this point on, the new subnet processes transactions involving the state in the subnet independent to the root chain. Further subnets can then be spawned from any point in the hierarchy. 

From the perspective of a peer in the network spawning or syncing with a new subnet starts a set of new processes to handle the independent state, mempool, and the specific [GossipSub](https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.1.md) topic to broadcast and receive subnet-specific messages.

> Stack of an HC node
![](https://hackmd.io/_uploads/BJla0JLYq.png)

Subnets are able to interact with the state of other subnets (and that of the rootnet) through _[cross-subnet](#Cross-net-messages "Cross-net messages")_ (or, simply,  _cross-net_) messages. __Full-nodes and validators in a given subnet need trusted access to the state of its parent subnet.__ We implement this by having them synchronise the chain of the parent subnet (i.e. child subnet full-nodes also run full nodes on the parent subnet). 
 
As it may be hard to enforce an honest majority of validators in every subnet, which can result in the subnet chain being compromised or attacked, the system provides a __firewall_ security property__. This guarantees that, for token exchanges, the impact of a child subnet being compromised is limited to, in the worst case, its circulating supply of the native token, determined by the (positive) balance between cross-net transactions entering the subnet and cross-net transactions leaving the subnet. Addresses in a subnet are funded through [cross-net transactions] that inject tokens into the subnet. In order for users to be able to spawn a new subnet, they need to deposit __initial collateral__ into the new subnet's parent. This collateral offers a minimum level of trust to new users injecting tokens into the subnet and can be slashed in case of misbehavior by subnet validators.

Validators in subnets are rewarded with fees for the transactions executed in the subnet. Subnets can run any consensus algorithm of their choosing, provided it can meet a defined interface and determine the consensus proofs they want to include for light clients (i.e. nodes that do not synchronize and retain a full copy of the blockchain and thus do not verify all transactions). Subnets periodically commit a proof of their state in their parent through [checkpoints](#Checkpointing "Checkpointing"). These proofs are propagated to the top of the hierarchy, making them accessible to any member of the system. They should include enough information that any client receiving it is able to verify the correctness of the subnet consensus. Subnets are free to choose a proof scheme that suits their consensus best (e.g. multi-signature, threshold signature, SPV (Simple Verification) or ZK (zero-knowledge) proofs, etc.). With this, users are able to determine the level of trust over a subnet according to the security level of the consensus run by the subnet and the proofs provided to light clients. Checkpoints are also used to propagate to other subnets in the hierarchy the information pertaining to cross-net messages.

The two key modules that implement all the logic for hierarchical consensus are:
- __[Subnet actor (SA)](#Subnet-Actor-SA "Subnet Actor (SA)")__: A user-defined actor deployed in the parent subnet from which the subnet wants to be spawned and that implements the subnet actor interface with the core logic and governing policies for the operation of the subnet. 
- __[The Subnet Coordinator Actor (SCA)](#Subnet-Coordinator-Actor-SCA "Subnet Coordinator Actor (SCA)")__: A system actor deployed in genesis (i.e. builtin-actor) in every HC-compatible subnet. The SCA implements the logic of the HC protocol and handles all the interactions with the rest of the system and their lifecycle. It is included as an additional builtin-actor in the builtin-actors bundle.

> Snapshot of three subnets with their corrsponding actors.
![](https://hackmd.io/_uploads/ByfPG7IYq.png)

The reference implementation of both actors in Filecoin currently target the FVM. The SCA is implemented as an additional ` builtin-actor` while SCA is an FVM user-defined actor.

## Subnet Actor (SA)
The Subnet Actor interface the core functions and basic rules required for an actor to implement the logic for a new subnet. This approach gives users total flexibility to configure the consensus, security assumption, checkpointing strategy, policies, etc. of their new subnet so it fulfills all the needs of their use case.

The Subnet Actor is the public contract accessible by users in the system to determine the kind of child subnet being spawned and controlled by the actor. From the moment the SA for a new subnet is spawned in the parent chain, users looking to participate from the subnet can instantiate their new chain and even start mining on it. However, in order for the subnet to be able to interact with the rest of the hierarchy, it needs to be registered by staking an amount of native tokens over the `CollateralThreshold` in the parent's SCA _(see [Collateral and slashing](#Collateral-and-slashing "Collateral and slashing"))_.

##### Subnet Actor Interface
A reference implementation for the subnet actor interface exists, but users are permitted to implement custom governing policies and mechanics that better suit their needs (e.g. request a dynamic collateral for validators, add a leaving fee coefficient to penalize validators leaving the subnet before some time frame, require a minimum number of validators, include latency limits, etc.).

> Interface every subnet actors needs to implement. These functions
> are triggered when a `message` is sent for their corresponding `methodNum`. 
```go
type SubnetActor interface{
    // Initializes the state of the subnet actor and sets
    // all its initial parameter.
    // (methodNum = 1)
    Constructor(ConstructParams)
    
    // It expects as `value` the amount of collateral the 
    // source wants to stake to become part of the subne.
    // It triggers all check to see determine if the source is elegible
    // to become part of the subnet, and must propagate an `AddCollateral` message
    // to the SCA to trigger the state.
    // 
    // Join is also responsible to send a `Register` message to the SCA
    // whenever the `CollateralThreshold` is reached. This function can also
    // be used to AddCollateral for the subnet in the SCA. Additional
    // checks for this operation may be included. As a result of the
    // execution an `AddCollateral` message must be sent to the SCA 
    // including the added collateral
    // (methodNum = 2)
    Join()
    
    // Called by participants that want to leave the subnet. It triggers all
    // the checks to see if the source is eligible to leave the subnet.
    // This function must propagate a `ReleaseCollateral` message in SCA to 
    // return their collateral to the actor so a message can be triggered
    // from the actor to return it back to its owner.
    // (methodNum = 3)
    Leave()
    
    // Kill performs all the sanity-checks required before completely
    // killing a subnet. It must propagate a `Kill` message to the SCA
    // to unregister the subnet from the hierarchy (making it no longer)
    // discoverable.
    // (methodNum = 4)
    Kill()
    
    // SubmitCheckpoint is called by validators looking to submit a
    // signed checkpoint for its propagation. This function performs all the
    // subnet-specific checks required for the final commitment of the 
    // checkpoint in the SCA (e.g. in the reference implementation of
    // the SubnetActor, SubmitCheckpoints waits for more than 2/3 of the validators
    // to sign a valid checkpoint to propagate it to the SCA).
    // 
    // This function must propagate a `CommitChildCheckpoint` message to the SCA
    // to commit the checkpoint.
    // (methodNum = 5)
    SubmitCheckpoint(Checkpoint)
    
    // CheckEquivocation is called by the SCA to perform consensus-specific
    // checks when an agreement equivocation is reported. It receives as input
    // the chain of the last `finality_delay` blocks including the invalid
    // blocks and the chain with what is supposed to be the valid block.
    // (methodNum = 6)
    CheckEquivocation(invalid []Block, valid []Block)
}
```
##### SubnetActor State
> Example of state of the subnet actor from the reference implementation.
```go
type SubnetState struct {
    // Human-readable name of the subnet.
    Name string
    // ID of the parent subnet
    ParentID address.SubnetID
    // Type of Consensus algorithm.
    Consensus hierarchical.ConsensusType
    // Minimum stake required for an address to join the subnet
    // as a miner
    MinMinerStake abi.TokenAmount
    // List of miners in the subnet.
    // NOTE: Consider using AMT.
    Miners []address.Address
    // Total collateral currently deposited in the
    TotalStake abi.TokenAmount
    // BalanceTable with the distribution of stake by address
    Stake cid.Cid // HAMT[tokenAmount]address
    // State of the subnet (Active, Inactive, Terminating)
    Status Status
    // Genesis bootstrap for the subnet. This is created
    // when the subnet is generated.
    Genesis []byte
    // Checkpointing period. Number of epochs between checkpoint commitments
    CheckPeriod abi.ChainEpoch
    // Checkpoints submit to SubnetActor per epoch
    Checkpoints cid.Cid // HAMT[epoch]Checkpoint
    // CheckpointVotes includes the validator votes for the checkpoint
    // of the current window.
    CheckpointVotes cid.Cid // HAMT[cid]CheckVotes
    // ValidatorSet is a set of validators
    ValidatorSet []hierarchical.Validator
    // MinValidators is the minimal number of validators required to join before starting the subnet
    MinValidators uint64
}
```
##### Constructor Parameters
> Constructor Parameters for reference implementation of subnet actor.
```go
type ConstructParams struct {
    // ID of the current network
    NetworkName     address.SubnetID      
    // Human-readable name for the subnet
    Name            address.SubnetID  
    // Consensus implemented in the subnet
    Consensus hierarchical.ConsensusType
    // Arbitrary consensus parameters required to initialize
    // the consensus protocol (e.g. minimum number of validators).
    // These parameters are consensus-specific.
    ConsensusParams *hierarchical.ConsensusParams
    // Minimum amount of stake required from participant 
    // to become a validator of the subnet.
    MinValidatorStake   abi.TokenAmount
    // Checkpointing period used in the subnet. It determines
    // how often the subnet propagates and commits checkpoints in its
    // parent
    CheckPeriod     abi.ChainEpoch
}
```
> TODO: There is an on-going revision of `ConstructParams` to include a way to provide arbitrary input arguments to a subnet.

## Subnet Coordinator Actor (SCA)
The main entity responsible for handling all the lifecycle of child subnets in a specific chain is the Subnet Coordinator Actor (`SCA`). The `SCA` is a builtin-actor that exposes the interface for subnets to interact with the hierarchical consensus protocol. This actor includes all the available functionalities related to subnets and their management. It also enforces all the security assumptions, fund management, and cryptoeconomics of the hierarchical consensus, as Subnet Actors are user-defined and can't be (fully) trusted. The `SCA` has a reserved address ID `f064`.

The MVP implementation of this builtin-actor can be found [here](https://github.com/adlrocha/builtin-actors/tree/master/actors/hierarchical_sca). The `SCA` exposes the following functions:


##### SCA Functions
> Functions of the SCA. These functions are triggered when a `message` is sent for their corresponding `methodNum`.
```go
type SCA interface{
    // Initializes the state of the SCA and sets
    // all its initial parameter.
    // (methodNum = 1)
    Constructor(ConstructParams)
    
    // Register expects as source the address of the subnet actor of
    // the subnet that wants to be registered. Its
    // `value` an amount of collateral over the `CollateralThreshold`.
    // This functions activates the subnet and from there on other
    // subnets in the system are allowed to interact with it and the
    // subnet can start commtting its checkpoints.
    // (methodNum = 2)
    Register()
    
    // AddCollateral expects as source the address of the subnet actor
    // for which the collateral wants to be added.  Its `value` should
    // include the amount of collateral to be added for the subnet.
    // (methodNum = 3)
    AddCollateral()
    
    // ReleaseCollateral expects as source the address of the subnet actor
    // for which the collateral wants to be released. It triggers a message
    // to the subnet actor returning the corresponding collateral. 
    // (methodNum = 4)
    ReleaseCollateral(value abi.TokenAmount)
    
    // Kill expects as source the address of the subnet actor to be killed.
    // This function can only be executed if no collateral or circulating
    // supply is left for the subnet (i.e. balance = 0).
    // (methodNum = 5)
    Kill()
    
    // Kill expects as source the address of the subnet actor for which the
    // checkpoint is being committed. The function performs some basic checks
    // to ensure that checkpoint is valid and it persist it in the SCA state.
    // (methodNum = 6)
    CommitChildCheckpoint(ch Checkpoint)
    
    // Fund can be called by any user in a subnet and it injects 
    // the `value` of native tokens included in the message to the source's address in
    // the child subnet given as argument.
    // (methodNum = 7)
    Fund(address.SubnetID)
    
    // Release can be called by any user in a subnet to release the amount 
    // of native tokens included in `value` from its own address in the
    // subnet to the address in the parent. 
    // (methodNum = 8)
    Release()
    
    // SendCross can be called by any user in the subnet to send 
    // an arbitrary cross-message to any other subnet in
    // the hierarchy.
    // (methodNum = 9)
    SendCross(msg CrossMsgParams)
    
    // ApplyMessage can only be called as an `ImplicitMessage` by
    // the `SystemActor` and is used to perform the execution of a 
    // of cross-net messages in the subnet. 
    // (methodNum = 10)
    ApplyMessage(msg CrossMsgParams)
    
    // InitAtomicExec can be called by users to initiate an
    // atomic execution with some other subnet.
    // (methodNum = 11)
    InitAtomicExec(params AtomicExecParams)
    
    // SubmitAtomicExec has to be called by all participants in an
    // atomic execution to submit their results and trigger the 
    // propagation of the output (or the abortion) of the execution
    // to the corresponding subnets.
    // (methodNum = 12)
    SubmitAtomicExec(submit SubmitExecParams)
    
    // WIP: Not implemented yet.
    // (methodNum = 13)
    ReportMisbehavior()
    
    // WIP: Not implemented yet.
    // (methodNum = 14)
    Save()
```

> All function parameters from the above snippet of code are fully specified in the detailed description of the different protocols.

##### SCA State
> State of the SCA
```go
type SCAState struct {
    // ID of the current network
    NetworkName address.SubnetID
    // Total of active subnets spawwned from this one
    TotalSubnets uint64
    // Minimum stake required to create a new subnet
    CollateralThreshold abi.TokenAmount
    // List of subnets
    Subnets cid.Cid // HAMT[cid.Cid]Subnet
    // Checkpoint period in number of epochs for the subnet
    CheckPeriod abi.ChainEpoch
    // Checkpoints committed in SCA
    Checkpoints cid.Cid // HAMT[epoch]Checkpoint
    // CheckMsgMetaRegistry
    // Stores information about the list of messages and child msgMetas being
    // propagated in checkpoints to the top of the hierarchy.
    CheckMsgsRegistry cid.Cid // HAMT[cid]CrossMsgs
    // Latest nonce of a cross message sent from subnet.
    Nonce             uint64  
    // BottomUpNonce of bottomup messages for msgMeta received from che    kpoints.
    // This nonce is used to mark with a nonce the metadata about cross-net
    // messages received in checkpoints. This is used to order the
    // bottom-up cross-messages received through checkpoints.
    BottomUpNonce     uint64
    // Queue of bottom-up cross-net messages to be applied.
    BottomUpMsgsMeta  cid.Cid // AMT[schema.CrossMsgs]
    // AppliedNonces keep track of the next nonce of the message to be applied.
    // This prevents potential replay attacks.
    AppliedBottomUpNonce uint64
    AppliedTopDownNonce  uint64
    // Registry with all active atomic executions being orchestrated
    // by the current subnet.
    AtomicExecRegistry cid.Cid // HAMT[cid]AtomicExec
}
```

> Struct with the information the SCA keeps for each child subnet
```go
// Subnet struct kept by the SCA with the information of
// all of its children.
type Subnet struct {
    // ID of the Subnet
    ID          address.SubnetID 
    // Parent ID
    ParentID    address.SubnetID
    //  Collateral staked for this subnet.
    Collateral       abi.TokenAmount
    // List of cross top-down messages committed for the subnet..
    TopDownMsgs cid.Cid // AMT[ltypes.Messages] 
    // Latest nonce of cross message submitted to subnet.
    Nonce      uint64
    // Amount of native tokens injected in the subnet and
    // that can be used freely in the subnet.
    CircSupply abi.TokenAmount 
    // Status of the checkpoint (`Active`, `Inactive`, etc.)
    Status     Status
    // Latest checkpoint committed for the subnet.
    // Kept for verification purposes.
    PrevCheckpoint schema.Checkpoint
}
```

## Consensus Interface
Each subnet can run its own implementation of a consensus algorithm. In order for different consensus implementations to operate semlessly with the Filecoin stack, we decouple the core methods of the current consensus in its own interace. In order for a consensus implementation to be usuable in a subnet it needs to implement this interface.
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
    // Return the type of consensus. 
    Type() hierarchical.ConsensusType
}
```
An example implementation of a BFT-like consensus protocol for HC can be found [here](https://github.com/filecoin-project/mir)

## Lifecycle of a subnet
The following section presents an overview of the lifecycle of a subnet.

### Spawning and joining a subnet
Creating a new subnet instantiates a new independent state with all its subnet-specific requirements to operate independently. This includes, in particular: a new pubsub topic that peers use as the transport layer to exchange subnet-specific messages, a new mempool instance, a new instance of the Virtual Machine (VM), as well as any other additional module required by the consensus that the subnet is running (builtin-actors, mining resources, etc.). 

To spawn a new subnet, peers need to deploy a new `SubnetActor` that implements the core logic for the governance of the new subnet. The contract specifies the consensus protocol to be run by the subnet and the set of policies to be enforced for new members, leaving members, checkpointing, killing the subnet, etc. For a new subnet to interact with the rest of the hierarchy, it needs to be registered in the `SCA` of the parent chain. The `SCA` is a system actor that exposes the interface for subnets to interact with the hierarchical consensus protocol. This smart contract includes all the available functionalities related to subnets and their management. And, as `SA`s are user-defined and untrusted, it also enforces security assumptions, fund management and the cryptoeconomics of hierarchical consensus.

Subnets are identified with a unique ID that is inferred deterministically from the ID of its ancestor and from the ID of the `SA` that governs its operation. This deterministic naming enables the discovery of --- and interaction with --- subnets from any other point in the hierarchy without the need of a discovery service: peers need only send a message to the subnet's specific pubsub topic, identified with the subnet's ID.

For a subnet to be registered in the `SCA`, the actor needs to send a new message to the `Register()` function of the `SCA`. This transaction includes the amount of tokens the subnet wants to add as collateral in the parent chain to secure the child chain. To perform this transaction, the `SA` should have enough funds available, other peers need to have joined and staked in the `SA` according to its policy to fund the register transaction. For a subnet to be activated in HC, at least `CollateralThreshold` needs to be staked in the `SCA`.

### Leaving and killing a subnet
Members of a subnet can leave the subnet at any point by sending a message to the subnet's `SA` in the parent chain. If the miner fulfils the requirements to leave the subnet defined in the subnet's `SA` when it was deployed, a message to the `SCA` is triggered by the `SA` to release the miner's collateral.  If a miner leaving the subnet brings the collateral of the subnet below `CollateralThreshold`, the subnet gets in an `Inactive` state, and it can no longer interact with the rest of chains in the hierarchy or checkpoint to the top chain. To recover its `Active` state, users of the subnet need to put up additional collateral.

Validators of a subnet can also kill a subnet by sending a `ReleaseCollateral()` message to the `SA`. Similar to the previous situation, the `SA` sends a message to the `SCA` to release all the collateral for the subnet if all the requirements to kill the subnet are fulfilled.

Subnet validators need to have locked at least `CollateralThreshold` in their parent's `SCA` to register the subnet to the hierarchy and be able to interact with other subnets. This collateral is frozen through the lifetime of the subnet and does not become part of its circulating supply. These funds are slashed when a valid complaint in the subnet is reported to the parent. If the subnet's collateral drops below `CollateralThreshold`, the subnet enters an `Inactive` state, and it can no longer interact with the rest of the hierarchy. To recover its `Active` state, users of the subnet need to put up additional collateral.

### Handling the state of killed subnets
Validators in a subnet may choose to implicitly kill it by stopping the validation of blocks. The subnet may still be holding user funds or useful state. If miners leave the subnet and take the collateral below the `CollateralThreshold`, users no longer have a way to get their funds and state out of the subnet. To prevent this from happening, the `SCA` includes a `Save()` function that allows any participant in the subnet to persist the state. Users may choose to perform this snapshot with the latest state right before the subnet is killed, or perform periodic snapshots to keep track of the evolution of the state. Through this persisted state and the checkpoints committed by the subnet, users are able to provide proof of pending funds held in the subnet or of a specific part of the state that they want to be migrated back to the parent. `Save()` is also used to enforce the [Data availability](#Data-availability "Data availability") of a subnet's state.

## Naming
Every subnet is identified with a unique `SubnetID`. This ID is assigned deterministically and is inferred from the `SubnetID` of the parent and the address of the subnet actor in the parent responsible for governing the subnet. The rootnet in HC always has the same ID, `/root`. From there on, every subnet spawned from the root chain is identified through the address of their `SA`. Thus, if a new subnet is being registered from an actor with ID `f0100`, the subnet is assigned an ID `/root/f0100`. Actor IDs are unique through the lifetime of a network. Generating subnet IDs using the `SA` ID ensures that they are unique throughout the whole history of the system.

The assignment of IDs to subnets is recursive, so the same protocol is used as we move deeper into the hierarchy. A subnet represented by `SA` with address `f0200` spawned in `/root/f0100` is identified as `/root/f0100/f0200`. To create the subnet ID to any subnet we just need to add the address of its subnet actor as a suffix to its parent's ID. 

This naming convention allows to deterministically discover and interact with any subnet in the system. It also offers an implicit map of the hierarchy. Peers looking to interact with a subnet only need to know their `SubnetID`, and publish  a message to the pubsub topic with the same name. 

Peers participating in a subnet are subscribed to all subnet-specific topics and are able to pick up the message. Subnet-specific pubsub topics are named also deterministically by using the subnet's ID as a suffix to the topic. Thus, subnets spawn (at least) three different topics for their operation: the `/fil/msgs/<subnetID>` topics to broadcast mempool messages; the `/fil/blocks/<subnetID>` topic to distribute new blocks; and the `/fil/resolver/<subnetID>` topic where cross-net content resolution messages are exchanged. These topics for subnet `/root/f0100` are identified as `/fil/msgs/root/f0100`, `/fil/blocks/root/f0100`, `/fil/resolver/root/f0100`, respectively.

Peers can also poll the available child chains of a specific subnet sending a query to the `SCA` requesting to list its children. This allows any peer to traverse the full hierarchy and update their view of available subnets.

In the future, HC may implement an additional DNS-like actor in the system that allows the discovery of subnets using human-readable names, thus making the transaction between a domain name and the underlying ID of a subnet.

### SubnetID
`SubnetID`s are the unique identifiers of subnets. While its string representation resembles a path directory (see examples above), the following objects is used for its byte and in-memory representation (its serialized representation, is the CBOR marshalling of this object):
```go
type SubnetID struct {
    // string representation of the parent SubnetID
    Parent string 
    // Address of the subnet actor governing the operation
    // of the subnet in the parent.
    // (it must be a an ID address)
    Actor address.Address
}
```

`SubnetID` includes the following convenient methods to aide in the use of `SubnetID`s.
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
CommonParent(subnet.ID) Subnet.ID
// Returns the next subnet down in the hierarchy in the path given in 
// the current SubnetID from the one given as an argument. It errors
// if there is not way to go down the path from the given argument.
// 
// Example: 
// `/root/f0100/f0200`.Down(`/root`) = `/root/f0100`
Down(subnetID) (SubnetID, error)
// Returns the next subnet up in the hierarchy in the path given in 
// the current SubnetID from the one given as an argument. It errors
// if there is not way to go up the path from the given argument.
// 
// Example: 
// `/root/f0100/f0200`.Up(`/root/f0100`) = `/root`
Up(subnetID) (SubnetID, error)
```

## Hierarchical Address
HC uses [Filecoin addresses](https://spec.filecoin.io/#section-appendix.address) for its operation. In order to deduplicate addresses from different subnets, HC introduces a new address protocol with ID `4` called _hierarchical address (HA)_. A hierarchical address is just a raw Filecoin address with additional information about the subnet ID the address refers to. 

There are 2 ways a Filecoin address can be represented. An address appearing on chain will always be formatted as raw bytes. An address may also be encoded to a string, this encoding includes a checksum and network prefix. An address encoded as a string will never appear on chain, this format is used for sharing among humans. A hierarchical address has the same structure of a plain Filecoin address but its payload is a 140 bytes fixed-length array conformed by:
- __Levels (1 byte)__: Represents the number of levels in the `SubnetID` included the address. This is exclusively used to avoid having large string addresses when the number of levels of the `SubnetID` is small and the HA payload includes a lot of padded zeros at the end.
- __SubnetID (74 bytes)__: String representation of the subnet ID (e.g. `/root/f01010`). The maximum size is set to support at most 3 levels of subnets using subnet IDs with the maximum id possible (which may never be the case, so effectively this container is able to support significantly more subnet levels). The size of `/root` is 5 bytes, and each new level can have at most size `23` (`22` bytes for the number of characters of the `MAX_UINT64` ID address and 1 byte per separator).
> TODO: We could compress by making using varints instead of the string representation for IDs in `SubnetID`
- __Separator (1 byte)__: One character used to separate the Subnet ID from the raw Filecoin address. The specific separator used for HC is the`:` string.
- __RawAddress (up to 66 bytes)__: Byte representation of the raw Filecoin address. The maximum size is determined by the size of the SECPK address.
- __End character (1 byte)__: One character used to flag the end of the useful payload and the beginning of the zero padding up to the 140 bytes fixed-length of the address payload. The specific end character used for HC is the `,`.

> Structure of Hierarchical Address
```
|----------|-----------------------------------------------------------------------------------------------------------------------------------|
| protocol |                                                            payload                                                                |
|----------|-----------------------------------------------------------------------------------------------------------------------------------|
|    4     | levels (1 byte) | subnetID (up to 74 bytes) | separator (1 byte) | raw address (up to 66 bytes) | end (1 byte) | optional padding |
|----------|-----------------------------------------------------------------------------------------------------------------------------------|
```

The payload of an HA looks something like:
```
| /root/f01001 | : | <payload raw address bytes> | , | optional zero padding``
```

With hierarchical addresses three new functions are introduced to Filecoin addresses:
- `Raw()`: Returns the raw address of the hierarchical address. If it is not an HA, it still returns the corresponding raw address.
- `Subnet()`: It returns the subnet ID of the HA. It returns an error or an `Subnet.Undef` if the address is not an HA.
- `Levels()`: Returns the number of levels in the `SubnetID` included in the HA address.
- `PrettyString()`: Returns a beautified version of an HA address like `/root/f0100:<raw address>`. This is method is only available for HA. For the rest of addresses it just returns `String()`. 

The string representation of HA addresses is encoded as every other Filecoin address (see [spec](https://spec.filecoin.io/#section-appendix.address.string)) with the difference that the size of the payload used to encode the string representation of the address differs to remove unnecessary padding. Thus, the byte payload from the address is truncated to the following size `HA_ROOT_LEN + (NUM_LEVELS - 1) * HA_LEVEL_LEN` before encoding the string address where `NUM_LEVELS` is the number of levels in the `SubnetID` of the address and `HA_ROOT_LEN = 5` and `HA_LEVEL_LEN = 23`;

Finally, a pair of keys from a user control the same address in every subnet in the system. Thus, the raw address determines the ownership of a specific HA. 

## Checkpointing
Checkpoints are used to anchor a subnet's security to that of its parent network, as well as to propagate information from a child chain to other subnets in the system. Checkpoints for a subnet can be verified at any point using the state of the subnet chain which can then be used to generate proofs of misbehaviors in the subnet (or so-called _fraud/fault proofs_) which, in turn, can be used for penalizing misbehaving entities (_"slashing"_). See [detectable misbehaviors](#Detectable-misbehaviors "Detectable misbehaviors") for further details.

Checkpoints need to be signed by miners of a child chain and committed to the parent chain through their corresponding `SA`. The specific signature policy is defined in the `SA` and determines the type and minimum number of signatures required for a checkpoint to be accepted and validated by the `SA` for its propagation to the top chain. Different signature schemes may be used here, including multi-signatures or threshold signatures among subnet miners. For instance, in the reference implementation of `SA`, the actor waits for more than `2/3` of the validators in the subnet to send the valid checkpoint signed before propagating it to the `SCA` for commitment. Alternative verification policies for a subnet can be implemented in the `SubmitCheckpoint()` function of the subnet actor interface. 

In order for a new checkpoint to be accepted for commitment in `SCA`, the source of the message `CommitChildCheckpoint()` needs to be the address of the subnet actor of the corresponding subnet; the subnet needs to be in an `Active` state (i.e. its collateral is over `CollateralThreshold`); the epoch of the checkpoint should be a multiple of `CheckPeriod` and larger that that of the previous checkpoint; and the checkpoint must point to the `CID` of the previous checkpoint committed by the subnet. 

When spawned, subnets are allowed to configure the `CheckpointPeriod` that better suits their needs and the specifics of its consensus algorithm.

### Checkpoint Commitment
As an example, lets consider a checkpoint for subnet `/root/f0100/f0200`. Every `CheckPeriod` (in terms of subnet block time), validators access the checkpoint template that needs to be signed and populated by calling the `CheckpointTemplate()` state accesor from `SCA` in `/root/f0100/f0200`. Once signed and populated, checkpoints from `/root/f0100/f0200` are submitted to the `SA` with ID `f0200` of the subnet network `/root/f0100` by sending a message to `SubmitCheckpoint()`. After performing the corresponding checks and waiting for the commitment conditions (i.e. `2/3` of the validators sending a signed checkpoint in its reference implementation), this actor then triggers a message to `/root/f0100` `SCA`'s `CommitChildCheckpoint()` function to commit the checkpoint.

When the checkpoint is committed, `SCA` in `/root/f0100` is responsible for aggregating the checkpoint from `/root/f0100/f0200` with those of other children of `/root/f0100`, and for generating a new checkpoint for `/root/f0100` that is then propagated to its parent chain, `/root`. The committment of checkpoints also triggers the execution and propagation of cross-net messages. As checkpoints flow up the chain, the `SCA` of each chain picks up these checkpoints and inspects them to propagate potential state changes triggered by messages included in the cross-net messages that have the `SCA`'s subnet as a destination subnet (see [Cross-net messages](#Cross-net-messages "Cross-net messages")).

Every checkpoints for a subnet points to the previous checkpoint being committed to ensure their integrity.

> Checkpoint template state accessor in SCA
```go
// Returns the checkpoint template to be populated for the current
// checkpoint window. The current checkpoint window is computed by 
// (currEpoch / CheckPeriod) * CheckPeriod. This determines the checkpoint
// that needs to be populated and signed for the current window.
CheckpointTemplate()
```

As shown on the next figure, the checkpointing protocol has two distinct stages:
- __Checkpoint Window__: In this window the `SCA` opens a checkpoint template and starts populating it with cross-messages arriving to the subnet (and that need to be propagated further inside the checkpoint); and with the aggregation of checkpoints committed from the current network childrens. The checkpoint window for the checkpoint in epoch `n` starts at `n-CheckPeriod` and ends at epoch `n`.
- __Signing Window__: The signing window is the time range reserved for validators of the subnet to populate the checkpoint template with the corresponding proof of the state of the checkpoint, to sign the window, and to submitted to the corresponding `SA` in the parent for committment. The signing window for the checkpoint in epoch `n` goes from `n` to `n+CheckPeriod`. Consequently, the signing window for the checkpoint of epoch `n-CheckPeriod` and the checkpoint window for the checkpoint of epoch `n` is run in parallel. The checkpoint template provided by the `SCA` has `CrossMsgs`, `PrevCheck`, and `Epoch` already populated, and validators only have to add the corresponding `Proof` and sign it.


![](https://hackmd.io/_uploads/HkAodIuFc.png)

### Checkpoints data structure
Checkpoints are always identified though the [Content Identifier (CID)](https://github.com/multiformats/cid) of their `Data` (i.e. the payload of the checkpoint), and they can optionally include the corresponding signature from validators in the subnet chain (this can be the signature of an individual miner, a multi-signature, or a threshold signature, depending on the `SA` policy). The signature is never used for the computation of the CID of the checkpoint.

> Checkpoints Data Structure
```go

// Checkpoints wrap the checkpoint data and
// a field dedicated for the arbitrary signing policy
// usede by the subnet.
type Checkpoint struct {
    Data CheckpointData
    Sig []byte
}

// Data included in checkpoints
type CheckpointData struct {
    // Source subnet of the checkpoint.
    Source     address.SubnetID
    // Proof of the state of the subnet. In the
    // reference implementation this is the tipset
    // for the epoch in the checkpoint, but this could
    // be a ZKProof or any other proof chosen by the subnet.
    Proof     []byte
    // Epoch of the checkpoint. Determined by the
    // subnet's CheckPeriod
    Epoch     abi.ChainEpoch
    // Cid of the previous checkpoint committed for the subnet.
    PrevCheck cid.Cid
    // Array with the aggregation of all the checkpoints committed
    // from the subnet's children.
    Children  []ChildCheck
    // Array with cross-message metadata of messages being propagated
    // in the current checkpoint.
    CrossMsgs []CrossMsgMeta
}

// Metadata pointing to the list of messages being
// propagated in the checkpoint.
type CrossMsgMeta struct {
    // Source of the cross-messages included in
    // this metadata packagle
    From    address.SubnetID
    // Destination of the cross-messages included.
    To      address.SubnetID
    // CID of the aggregation of all the messages being
    // propagated. This CID is used to uniquely identify
    // this package of messages.
    MsgsCid cid.Cid
    // Nonce of the crossMsgMeta. It is used for partial
    // ordering and to prevent replay attacks.
    Nonce   uint64
    // Aggregation of all the native tokens being transacted
    // in the included messages.
    Value   abi.TokenAmount
}

// Package with all checkpoints committed in
// the checkpoint window from children.
type ChildChecks struct {
    // Source of the checkpoints. ID of the child.
    Source address.SubnetID
    // List of cid of the checkpoints committed by
    // the child in this checkpoint window.
    Checks []cid.Cid
}

```
Checkpoints include in their payload the following data:
- __`Source`__: The SubnetID of the subnet that is committing the checkpoint. The `SCA` checks that the right subnet actor is committing the checkpoint for the source to prevent forged checkpoints. 
- __`Proof`__: The proof of the state of the subnet that wants to be committed in the parent chain. In the reference implementation of the subnet actor we just includ the tipset for the epoch being committed, but this proof could be a snapshot of a test, a ZK Proof, or any other piece of information that subnet's want to anchor in their parents chain.
- __`Epoch`__: Epoch of the checkpoint being committed. The epoch must be a multiple of `CheckPeriod`.
- __`PrevCheck`__: `CID` of the previous checkpoint committed.
- __`Children`__: Slice of checkpoints from children propagated in the corrsponding checkpointing window.
- __`CrossMsgs`__: Metadata of all the messages being propagated in the checkpoint. This metadata includes the source, destination and `CID` of the messages. Every `CrossMsgMeta` gets updated with every new checkpoint on its way up the hierarchy aggregating messages with the same destination building a tree of linked message digests with different sources but same destination. Thus, every subnet only sees the message aggregation (i.e. the digest of all the subnets childrens CrossMsgMeta list) of its childs. Any subnet looking to know the specific messages behind the `CID` of a `CrossMsgMeta` -- which will be the case for the destination subnet of the messages, see [cross-net messages](#cross-net-messages) -- only need to send a query message leveraging the [Subnet Content Resolution Protocol](#Subnet-Content-Resolution-Protocol "Subnet Content Resolution Protocol") for the cross-msg `CID` to the corresponding pubsub topic of the source subnet. 

> TODO: Add a figure of how `CrossMsgMeta` are aggregated?

## Cross-net messages
Users in a subnet interact with other subnets through cross-net transactions (or messages). The propagation of a cross-net transaction may slightly differ depending on the location of subnets in the hierarchy (i.e. if moving up or down the hierarchy). In particular, we distinguish the following type of cross-net messages: 

- __Top-down messages__ _(brown)_ are cross-msgs directed towards a subnet that is lower in the hierarchy (e.g. from `/root/f0100` to `/root/f0200`).
- __Bottom-up  messages__ _(green)_ are cross-msgs directed towards a subnet that is higher in the hierarchy but shares the same prefix (e.g  from  `/root/f0100/f0200` to `root/f0100`).
- __Path messages__ _(pink)_. Every message routed in the hierarchy can be seen as a combination of top-down and bottom-up transactions. Path messages are cross-net messages in which the source and destination subnets are not in the same branch. These are propagated through bottom-up messages (i.e. `CrossMsgMeta` in checkpoints) up to the common parent (`/root`, in the worst case) and through top-down messages from there to the destination.

![](https://hackmd.io/_uploads/rJg6aduKq.png)

New cross-net messages from a subnet are sent by sending a message to the `SendCross()`, `Fund()`, or `Release()` functions of the `SCA` of the corresponding subnet. `SendCross()` sends an arbitrary message specified as an argument to the subnet in `Destination`; while `Fund()` initiates a top-down message to a child subnet with an amount of native tokens to the source's address in the subnet; and `Release()` sends and amount of native tokens to the source's address in the parent. When any of these messages is received, the `SCA` evaluates if it is a top-down or a bottom-up message, and routes it correspondingly (by notifying the children or including the message in a checkpoint, respectively).

### Cross-message pool
Nodes in subnets have two types of message pools: an internal pool to track unverified messages originating in and targeting the current subnet, and a `CrossMsgPool` that listens to unverified cross-msgs directed at (or traversing) the subnet. In order for cross-msgs to be verified and executied, they need to be run through the consensus algorithm of the subnet and included in a valid subnet block.

Full-nodes in subnets are required to be full-nodes of their parent in order to listen to events in their parent's `SCA` and their own subnet actor. The `CrossMsgPool` listents to the `SCA` and collects any new cross-net messages appearing the `SCA`. Whenever the subnet's parent`SCA` receives a new top-down message or collects a new bottom-up `CrossMsgMeta` from a child checkpoint, the `CrossMsgPool` is conveniently notified. Top-down messages can be proposed to and applied directly in the subnet. For bottom-up messages, the cross-msg pool only has the CID of the `CrossMsgMeta` that points to the cross-msgs to be applied and, therefore, needs to make a request to the [Subnet Content Resolution Protocol](#Subnet-Content-Resolution-Protocol "Subnet Content Resolution Protocol") to retrieve the raw messages, so they can be proposed and applied in the subnet. 

Blocks in subnets include both, messages originated within the subnet, and cross-msgs targeting (or traversing) the subnet. Both types can be differentiated by looking at the `From` and `To` of the messages: cross-net messages include `hierarchical address` (with subnet information) in both fields, while plain subnet messages include raw addresses in these fields. When a new block including top-down cross-msgs is verified in the subnet consensus, the cross-msgs are committed, and every node receiving the new block executes the cross-msgs to trigger the corresponding state changes and fund exchanges in the subnet.

### Cross-message execution
Cross-msgs in a block are implicitly executed by calling the `ApplyMsg()` of the subnet's `SCA` from the `SystemActor`. In the execution of a new block, the `TipSetExecutor` checks if the message to be applied is a plain subnet message or a cross-net message. If it is a cross-net message it tailors a new message to the `SCA` calling `ApplyMsg()` and including the cross-net message to be executed as a parameters. This new message is apply implicitly in the node with `ApplyImplicitMsg()` (see how messages to the `CronActor` and rewards are executed in the Filecoin spec).

What `ApplyMsg()` does to execute the cross-net message is:
- To check if it is a top-down or bottom-up message.
- According to its type, see if the message has the correct nonce according to the value of `AppliedTopDownNonce` and `AppliedBottomUpNonce`, respectively.
- Determine if the destination of the message is the current subnet or some other subnet in the hierarchy:
    - If the message is for the current subnet, the `From` and `To` of the cross-net message are translated into raw addresses, and a new `Send()` is called for the message in order to trigger the corresponding state changes in the subnet.
        - When the message is a top-down message, before the `Send()` of the cross-net messages, the amount of new tokens included in the `value` of the message (and that were locked in the `SCA` of the parent) need to be minted to allocate them to be used in the cross-net message. Thus, top-down messages mint new tokens in the subnet (with the consequent lock in the parent); while bottom-up messages burn native tokens in the subnet when they propagate bottom-up messages. 
    - If the message's destination is not the current subnet, the desination `Subnet` is checked to determine if it needs to be propagated as a top-down or a bottom-up messages, conveniently adding it in `TopDownMsgs`of the next subnet in the messages path to destination, or by including it in the next checkpoint, respectively.
- Increment the corresponding `AppliedNonces`.

### Top-down messages
When a new top-down cross-net message is sent to `SCA` by calling `Fund()`, or `SendCross()` with a destination which is down in the hierarchy, the `SCA` of the source subnet:
- Checks which child is the next subnet in the path to the messages destination.
- Assigns to the message the subsequent `Nonce` to the latest one used for that subnet. Every time a new top-down message to the subnet arrives, the `SCA` increments a nonce that is unique for every cross-net message to that destination. These nonces determine the total order of arrival of cross-msgs to the subnet; without them, different consensus nodes could execute different orderings, leading to nondeterminism. 
- It checks that that the `From` and `To` of the message include `HA` addresses with the right subnets. 
- It stores the message to notify its propagation in the `TopDownMsgs` of the corresponding child subnet.
- It locks the `SCA` the amount of native tokens included in the `value` of the message, increasing in the same amount the `CircSupply` of the subnet. These funds will be frozen until a bottom-up transaction releases them back to the parent. In this way, the `SCA` keeps track of the circulating supply of child subnets and is responsible for enforcing the firewall requirement in subnets (whenever native tokens want to be released from it. See [bottom-up messages](#bottom-up-messages).

When the new cross-message to a subnet is included in its `TopDownMsgs`, the validators of the subnet are notified through their `CrossMsgPool` about this new top-down message. The `CrossMsgPool` waits for a `FinailityThreshold` before proposing the message to be sure that the top-down message commitment can be considered final (this `finalityThreshold` may change according to the requirements of the subnet, and the specific consensus algorithm used by the parent. The `finalityThreshold` for BFT-like consensus may be `1` or close to `1`, while sync consensus algorithms like PoW may require larger thresholds). After the `finalityThreshold`, validators in the subnet will check the latest `AppliedTopDownNonce` to fetch all unverfied cross-net message to the latest one included in `TopDownMsgs`, and they will propose them for their inclusion in a block and subsequent execution. 

![](https://hackmd.io/_uploads/rynGK2ut5.png)


### Bottom-up messages

#### Including messages in `CrossMsgMeta`
Bottom-up messages are created by sending a message to the `Release()` method of the subnet's `SCA`, or to `SendCross()` including a message in `CrossMsgsParams` which is directed to some subnet in the upper layers of the hierarchy of with some other parent at the same level. Bottom-up messages are propagated inside checkpoints. At every checkpoint period, the `SCA` collects and aggregates all `CrossMsgMeta` from bottom-up transactions originated in the subnet, as well as all the `CrossMsgMeta`. All these `CrossMsgMeta`are included in the next checkpoint for their propagation up the hierarchy.

Whenever a new bottom-up message is triggered in a subnet, its `SCA`:
- Burns in the subnet the amount of native tokens included in the `value` of the message.
- Checks the checkpoint being populated in the current checkpoint window and checks if it already has a `CrossMsgMeta` with the same destination of the message.
    - If the `CrossMsgMeta` doesn't exist in the checkpoint, the SCA creates a new `CrossMsgs` appending the cross-net message in the `CrossMsgsRegistry` of the SCA, and includes in the checkpoint a new `CrossMsgMeta` for the destination including the `CID` of the `CrossMsgs` stored in the registry.
    - If the `CrossMsgMeta` for the destination exists in the checkpoint, the SCA gets from the `CrossMsgsRegistry` the current CID included in the `CrossMsgMeta`, and it appends in `Msgs` the new cross-net message created. `SCA` then updates with the new `CID` (after appending the message) to the `CrossMsgMeta` for the checkpoint, deletes the outdated `CrossMsgs` from the registry, and includes the updated one.
    - In these updates, also the total amount of native tokens included in the messages of the `CrossMsgMeta` is updated in the `Value` field.
- Finally, when the signing window for the checkpoint closes, the checkpoint is propagated including a link to the cross-message in the `CrossMsgMeta` of the checkpoint. 

> Bottom-up messages and checkpoint propagation data structures
```go

// Metadata pointing to the list of messages being
// propagated in the checkpoint.
type CrossMsgMeta struct {
    // Source of the cross-messages included in
    // this metadata packagle
    From    address.SubnetID
    // Destination of the cross-messages included.
    To      address.SubnetID
    // CID of the aggregation of all the messages being
    // propagated. This CID is used to uniquely identify
    // this package of messages.
    MsgsCid cid.Cid
    // Nonce of the crossMsgMeta. It is used for partial
    // ordering and to prevent replay attacks.
    Nonce   uint64
    // Aggregation of all the native tokens being transacted
    // in the included messages.
    Value   abi.TokenAmount
}

// CrossMsgs is the data structure used to persist in the
// `CrossMsgsRegistry` the `Msgs` and `CrossMsgMeta` 
// propagated in checkpoints
type CrossMsgs struct {
    // Raw msgs from the subnet
    Msgs  []Message   
    // Metas propagated from child subnets
    Metas []CrossMsgMeta 
}

// MetaTag is a convenient struct
// used to compute the Cid of the MsgMeta
type MetaTag struct {
    MsgsCid  cid.Cid
    MetasCid cid.Cid
}
```

#### Executing bottom-up messages
When a new checkpoint for child is committed in a network, the `SCA` checks if it includes any `CrossMsgMeta` before storing it in its state. If this is the case, it means that there are pending cross-msgs to be executed or propagated further in the hierarchy. For every `CrossMsgMeta` in the checkpoint `SCA`:
- Checks if the `Value` included in the `CrossMsgMeta` for the source subnet is below the total `CircSupply` of native tokens for the subnet. If the `Value > CircSupply`, `SCA` rejects the cross-msgs included in the `CrossMsgMeta` due to a violation of the firewall requirement. If `Value <= CircSupply` then the `CrossMsgMeta` is accepted, and `CircSupply` is decremented by `Value`.
- Checks if the destination of the `CrossMsgMeta` is the current subnet; a subnet higher up in the hierarchy; or a subnet that is down in the hierarchy.
    - If the `CrossMsgMeta` points to the current subnet or to some other subnet down the current branch of the hierarchy in its `To`, the `CrossMsgMeta` is stored with the subsequent `BottomUpNonce` in `BottomUpMsgsMeta` to notify the `CrossMsgPool` that the cross-msgs inside the `CrossMsgMeta` need to be conveniently executed (or routed down).
    - If the `CrossMsgsMeta` points to a subnet that needs to be routed up, `SCA` executes the same logic as when a new bottom-up cross-msg is created in the subnet, but appending the `CrossMsgsMeta` into the `Meta` field of `CrossMsgs`. The corresponding `CrossMsgsMeta` of the current checkpoint is created or updated to include this meta for it to be propagated further up in the next checkpoint. Thus, the `CID` of the new `CrossMsgMeta` for the parent includes a single `CID` that already aggregates a link to the `CrossMsgMeta` of the child with cross-messages that need to go even upper in the hierarchy.

Validators `CrossMsgPool`s also listen for new `BottomUpMsgsMeta` being included in their subnet SCA. When a new `CrossMsgsMeta` appear in `BottomUpMsgsMeta` (after the committment of a checkpoint), the `CrossMsgPool` checks if `CrossMsgsMeta.Nonce > AppliedBottomUpNonce` to see if it includes cross-msgs that haven't been executed yet. If this is the case, the `CrossMsgPool`:
- Gets all `CrossMsgsMeta` in `BottomUpMsgsMeta` with `Nonce > AppliedBottomUpNonce`.
- Gets `CrossMsgMeta.Cid` and makes a request to the subnet content resolution protocol to resolve the `CrossMsgs` behind that `CrossMsgMeta`. These requests are directed to the subnet in `Source` and they resolve the CID from the subnet's `CrossMsgsRegistry`. 
    - If the resolved `CrossMsgs` only includes elements in the `Msgs` field, they can be directly proposed in the next block for their execution.
    - If this is not the case, and `CrossMsgs` includes in its `Meta` field `CrossMsgMetas` from its children, then these `CrossMsgsMeta` need to be resolved recursively until all the `CrossMsgsMeta` have been resolved to their underlaying messages successfully.
- Then, as it happened for top-down messages, when the `CrossMsgPool`  has all the bottom-up messages to be applied, it waits for a `FinailityThreshold` before proposing the message to be sure that the checkpoint commitment can be considered final, and all the resolved cross-messages are proposed for their inclusion and subsequent execution. 

![](https://hackmd.io/_uploads/Bkrzj2uF5.png)

### Path messages
Path messages are propagated and executed as a combination of bottom-up and top-down messages according the path they need to traverse in the hierarchy. Let's consider a message from `/root/f0100/f0200` to `/root/f0100/f0300`. This message is propagated as a set of bottom-up message up to the closes common parent (`/root/f0100` in our example). When the checkpoint including the cross-message from `/root/f0100/f0200` arrives to `/root/f0100`, the `CrossMsgMeta` is resolved, and from there on, the message is propagated as a top-down message from the closest common parent to the destination (in this case, from `/root/f0100` to `/root/f0100/f0300`),

#### Errors propagating cross-net messages
If at any point the propagation or execution of a cross-msg fails (either because the message runs out of gas in-transit; because the message is invalid in the destination subnet; or because the `CrossMsgMeta.Cid` can't be resolved successfully), the message is discarded, and a error is tracked for the cross-message.

> TODO: Come up with error codes for message failures and how to propagate them to the source. Only the source will be notified.

### Minting and burning native tokens in subnets
Native tokens are injected to the circulating supply of a subnet by performing top-down messages. These messages lock the amount of tokens included in the `value` of the message in the `SCA` of the parent, and they trigger the minting of new tokens in the subnet when they are executed. To mint new tokens in the subnet, we include a new `SubnetMint` method with `methodNum=5` to the `RewardActor`. `SubnetMint` can only be called by the `SCA` in a subnet through `ApplyMsg()` method when executing a message. `SubnetMint` funds the `SCA` with enough minted native tokens to provide the destination address with its corresponding subnet tokens (see [sample implementation](https://github.com/filecoin-project/eudico/blob/bb52565105f7fe716463b1e09dad7492569089f5/chain/consensus/actors/reward/reward_actor.go#L94)).

Validators in subnets are exclusively rewarded in native-tokens through message fees, so the balance of the `RewardActor` in subnets is only used to increase the circulating supply in a subnet by order of the `SCA`. For new native tokens to be minted in a subnet, the same amount of tokens need to have been locked in the `SCA` of the parent.

> Note: This change of the reward actor is not required for the `rootnet`. We can have a custom bundle with the modified `RewardActor` to be used exclusively for subnets.

On the other hand, bottom-up messages release funds from a subnet (reducing its circulating supply). In this case, burning the funds from the subnet is straightforward. When the bottom-up messages are included in a checkpoint, the `SCA` triggers a message with the `value` amount of native-tokens to the `BurnActorAddress` of the subnet. Once the checkpoint is committed to the parent, and the messages executed, the same amount of native tokens will be released from the parent's `SCA` and conveniently sent to the destination addresses of the bottom-up messages.

    
## Subnet Content Resolution Protocol
For scalability reasons, when the destination subnet receives a new checkpoint with cross-msgs to be executed, it is only provided with the `CID` of the aggregated messages inside the `CrossMsgMeta`. For the subnet to be able to trigger the corresponding state changes for all the messages, it needs to fetch the payload of messages behind that `CID`, as illustrated in previous sections. The subnet `SCA` where the bottom-up message is generated keeps a `CrossMsgsRegistry` with all `CID`s for `CrossMsgsMeta` propagated (i.e. a content-addressable key-value store), used to fulfill content resolution requests.

Every subnet runs a specific pubsub topic dedicated to exchange Subnet Content Resolution messages. This topic always has the following ID: `/fil/resolver/<subnet_ID>`. So when a subnet receives a `CrossMsgMeta`, it only needs to tailor a query to the topic of the source subnet of the `CrossMsgMeta` for the `CID` of the messages included in it to resolve the messages.

The subnet content resolution protocol can be extended to resolve arbitrary content from the state of a subnet. Currently, the protocol includes handlers for the resolution by `CID` of the following objects.
- `CrossMsgMeta`: Digest of a
- `LockedStates`: The input state locked for an atomic execution (see [Atomic Execution Protocol](#Atomic-Execution-Protocol "Atomic Execution Protocol"))
- `Checkpoints`: Committed checkpoints of a subnet in the parent `SCA`

> TODO: Due to how the MVP was implemented, the content resolution protocol includes a large amount of message types (one per object resolution). This can be simplified and is expected to be done before moving the protocol into production. See the [following issue](https://github.com/filecoin-project/eudico/issues/146) for further details (once this is implemented the spec will be conveniently updated).

### Resolution approaches
The protocol implements two approaches to resolve content: 

- A __push__ approach, where, as the checkpoints and `CrossMsgMetas` move up the hierarchy, miners publish to the pubsub topic of the corresponding subnet the whole tree of `CrossMsgs` behind the `CrossMsgsMeta` `CID` including all the messages targeting that subnet. To push the message, the content resolver manager publishes a `Push` message in the resolver topic of the destination subnets specifying the type of content being pushed along with its CID. When new checkpoints are committed, source subnet's proactively push the content to the destination subnets for which `CrossMsgsMeta` have been included in the checkpoint. When validators and full-nodes in the subnet come across these `Push` messages, they may choose to pick them up and cache/store them locally for when the checkpoint with the `CrossMsgsMeta` directed to them arrives, or discard them (in which case, they will need to explicitly resolve the content when required).

- A __pull__ approach, where, upon a destination subnet receiving a checkpoint with cross-msgs directed to it, miners' `CrossMsgsPool`s publish a `Pull` message in the `Source` subnet's pubsub topic to resolve the cross-msgs for the specific `CID`s found in the tree of cross-msg meta. These requests are answered by publishing a new  resolve message in the requesting subnet with the corresponding content resolution. The source subnet answers to the resolver topic of the subnet originating the request with a `ResponseMeta` message including the resolution of the `CID`. This new broadcast of a content resolution to the subnet's pubsub channels gives every cross-msg pool a new opportunity to store or cache the content behind a `CID` even if they do not yet need it.

- A __peer-to-peer fallback__: These push and pull protocols operate through the broadcast of messages to the resolver topics of the corresponding subnets, but what if the propagation of these messages fail? As a last-resort fallback, HC peers include a peer-to-peer protocol to allow the direct request of `CrossMsgMeta` and other subent-related information. Peers can choose to directly request the resolution of content from peers they know are participating in the subnet holding the content. Peers can use the validators of a subnet as their endpoionts for this fallback as their `multiaddress` is published on-chain. Additionally, other peers (and external storage services) may advertize themselves as _"servers"_ of content for a subnet (see [data availability](#data-availability) for further details).
> Note: This fallback protocol is not implemented yet as part of the MVP.

All these approaches to content resolution include safe-guards to prevent DoS attacks.
- Messages that are equal to another message recently exchanged in the topic (independently of their source) are immediately rejected.
- Malformed messages are immediately rejected.
- Peers sending requests for non-existing `CID`s for a subnet are penalized.
- All `Response` and `Push` messages are self-certified. Peers sending content that doesn't correspond to the `CID` included in the message are penalized. 

> Content Resolver Message Types
```go
type MsgType enum (
// PushMeta content to other subnet
    PushMeta MsgType = iota
    // PullMeta requests CrossMsgs behind a CID
    PullMeta
    // ResponseMeta is used to answer to pull requests for cross-msgs.
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
	From address.SubnetID
	// Message type being propagated
	Type MsgType
	// Cid of the content
	Cid cid.Cid
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
Peers requesting content from others subnets trust that the peers in the other network from which a checkpoint with cross-msgs has been propagated will resolve the content resolution requests sent to the subnet. Intuitively, the node that triggered the cross-msg has no incentive on denying access to this data (as his funds have already been burnt), but data availability is an issue that is worth addressing further. The aforementioned design of the content resolution protocol assumes at least _one honest participant in the subnet_ (i.e. a peer that always answers successfully to content resolution requests) _and that the data in the subnet is always available_. In a real environment these assumption may not hold, and more complex schemes may be needed to incentivize subnet peers and ensure that every content resolution request between subnets is fulfilled, and a high-level of availability of data.

To overcome this issue, `SCA` in subnets include the `Save()` function and peers will implement a protocol to backup the state of the function in any storage system where data can be retrievable and available independently of the state of a subnet (let this be Filecoin storage, IPFS, or any other decentralized or centralized storage systems). Having the state always available is key for:
- The execution and validations of cross-net messages.
- Creating fraud/fault proofs from detectable misbehaviors in a subnet.
- Migrating the state of a subnet and spawning a new subnet from the existing state of another network.

> TODO: For this purpose, a `Persistence` interface will be explored and implemented in future iterations of the protocol. Ideally we should piggy-back from all the available storage in the Filecoin network, FVM native integration with storage primitives, and all the data retrievability work being done by [CryptoNetLab](https://research.protocol.ai/groups/cryptonetlab/) or [Filecoin Saturn](https://github.com/filecoin-project/saturn-node).

## Atomic Execution Protocol
An issue arises when state changes need to be atomic and impact the state of different subnets. A simple example of this is the atomic swap of two assets hosted in different subnets. The state change in the subnets needs to be atomic, and it requires from state that lives in both subnets. To handle these atomic transactions, the parties involved in the execution can choose any subnet in the hierarchy in which they both have a certain level of trust to migrate the corresponding state and orchestrate the execution. Generally, subnets will choose the closest common parent as the execution subnet, as they are already propagating their checkpoints to it and therefore leveraging shared trust.

A cross-net atomic execution takes tuples of input states and returns tuples of outputs states, which may belong to different subnets, but should appear as a single transaction in which all input/output states belong to the same subnet. The atomic execution protocol has the following properties: 

- __Timeliness__: The protocol  eventually completes by committing or aborting.
- __Atomicity__: If all involved subnets commit and no subnet aborts beforehand, the protocol commits, and all subnets involved have the output state available as part of their subnet state. 
  Otherwise, the protocol aborts and all subnets revert to their initial state.
- __Unforgeability__: No entity in the system (user or actor) is able to forge the inputs and outputs provided for the execution or the set of messages orchestrating the protocol.

Finally, the data structures used by the protocol need to ensure the __consistency__ of the state in each subnet (i.e. that the output state of the atomic execution can be applied onto the original state --- and history --- of the subnet without conflicts). That being said, it is worth noting that the _firewall requirement_ limits against the impact of an attack involve native token exchanges, but it can't protect against an attack over the state of a subnet (including non-native tokens). To cover against this kind of attacks the collateral is used (see [detectable misbehaviors](#Detectable-misbehaviors "Detectable misbehaviors")).

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
    Lock(rt runtime.Runtime, params *LockParams) cid.Cid
    // Merge takes external locked state and merges it to 
    // the current actors state.
    // (methodNum = 3)
    Merge(rt runtime.Runtime, params *MergeParams) *abi.EmptyValue
    // Finalize merges the output of an execution and unlocks the state.
    // (methodNum = 4)
    Finalize(rt runtime.Runtime, params *UnlockParams) *abi.EmptyValue
    // Abort unlocks the state and aborts the atomic execution.
    // (methodNum = 5)
    Abort(rt runtime.Runtime, params *LockParams) *abi.EmptyValue
    // StateInstance returns an instance of the lockable actor state
    StateInstance() LockableActorState
}
```
- The state of the actor needs to implement the `LockableActorState` interface that determines how to access persisted state from locked states and outputs from an execution. Actors supporting atomic executions are required to persist and make locked state retrieval for the operation of the protocol. In the reference implementation of the protocol, `LockableActor`s include a `LockedMapCID` HAMT that persists the locked state of all ongoing atomic executions where the key is the `CID`, that uniquely identifies the locked state, and the value is the `LockedState`. Of course, the actor state needs to be CBOR-deserializable. 
> LockableActorState interface
```go
type LockableActorState interface {
	cbg.CBORUnmarshaler
	// LockedMapCid returns the cid of the root for the locked map
	LockedMapCid() cid.Cid
	// Output returns locked output from the state.
	Output(*LockParams) *LockedState
}
```
- Any object of the state that needs to be lockable, has to implement the `LockableState` interface. The object needs to be CBOR-serializable (like any other actor state) and it needs to implement the desired merging logic (the strategy used to merge distinct states of the object in the state ---this logic is contract-specific---).
> `Lockablestate`interface.
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
Cid() cid.Cid
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
    Method abi.MethodNum
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
    - To start the execution, each party needs to lock, in their subnet, the state that will be used as input for the execution. This is done by sending a message to the `Lock()` function to the address of the `LockableActor` involved in the execution indicating in the `LockParams` the `MethodNum` and `Params` the parties agreed on for the atomic execution. `Lock()` returns the `CID` of the locked state and persists it in the corresponding `LockedStateRegistry` of the actor. Locking the state prevents new messages from affecting the state and leading to inconsistencies when the output state is migrated back. From now on, the actor won't accept any message involving the state locked. The locking of the input state in each subnet signals the beginning of the atomic execution.
    - One of the parties needs to initialize the execution by sending an `InitAtomicExec` message to the `SCA` of the parent responsible for orchestrating the execution specifying the `AtomicExecParams` (i.e. the list of messages and a map with the HA address and the `CID` of the input state for all the parties involved). If the initiator already has performed the off-chain execution (see next bullet), it can also submit the CID of its output state as part of the initialization message.
    - In its current implementation `SCA` verifies that is the common parent of all parties to accept the execution. To uniquely identify it computes the `CID` of the atomic execution (by computing the `CID` the `AtomicExecParams`). This `CID` identifies the atomic execution in the `SCA` through all its life. If the `InitAtomicExec` message succeed a new atomic execution is spawned for that CID in an `ExecInitialized` state.
> Note: At this point there's no deduplication of atomic executions in the same `SCA`. An atomic execution with the same `AtomicExecParams` can't be run twice in the same `SCA`. This is a limitation of the MVP implementation and it will be fixed in the next iteration by adding a nonce (see [issue](https://github.com/filecoin-project/eudico/issues/147).

- __Off-chain execution__: Each party only holds part of the state required for the execution. In order for the parties in the execution to be able to execute locally, they need to request the state locked in the other subnet. 
    - The `CID` of the input state is shared between the different parties in the execution during the initialization stage, and is leveraged by each party to request from the other subnets the locked input states involved in the execution. 
    - On the reception of the `CID` from the involved parties, peers can perform a request to the content resolution protocol for the `CID` of the input state in their source subnets by sending a `PullLocked` message. 
    - Once every input state is received for all the `CID`s of the input state involved in the execution, each party runs the execution off-chain to compute the output state. This execution is performed by creating a temporal view of the state of the contract and merging the locked state from the other subnets. With the state ready, the every message of the atomic execution are implicitly applied ([see code](https://github.com/filecoin-project/eudico/blob/bb52565105f7fe716463b1e09dad7492569089f5/chain/consensus/hierarchical/atomic/exec/exec.go#L32) for further details).
    - The `OutputState` for the execution is then returned for its commitment in the common parent.

- __Commit atomic execution in parent subnet__: As the parties involved perform the off-chain execution of `OutputState`, they commit it in the `SCA` of the parent subnet. 
    - The commitment is performed by sending a message to the `SubmitAtomicExec` of the `SCA` in the common parent using `SubmitExecParams` as an input. In `SubmitExecParams` users need to include their `LockedState` for the `OutputState` after the execution, and the `CID` of the atomic execution they are submitting.
    - The `SCA` checks that the `CID` of the `LockedState` matches the one submitted by the other parties, and accepts the submission. The execution will stay in an `ExecInitialized` state until all the parties submit the right `LockedState` as an `OutputState`. When this happens, the execution is marked as `ExecSuccess` and the `SCA` triggers a top-down message to the corresponding subnet to the `Merge` function of the `LockableActor` involved in the execution on every subnet. This will trigger the merge the of the `OutputState` and the unlock of the locked state.
    -  To prevent the protocol from blocking if one of the parties disappears halfway or is malicious, any party is allowed to abort the execution at any time by sending a `SubmitAtomicExec` message to the corresponding `SCA` setting the `Abort` field of `SubmitExecParams` to true. This moves the execution to an `ExecAbort` state in the `SCA`, and triggers a new top-down message to the `Finalize()` function of the `LockableState` involved in the execution on every subnet. These messages unlock the input state in the source subnets without merging any `OutputState` for the atomic execution. 

- __Termination__  When the `SCA` receives the commitment of all the computed output states, and if they all match, the execution is marked as successful, possible aborts are no longer taken into account, and subnets are notified, through a top-down message, that it is safe to incorporate the output state and unlock the input state (see details above). If, instead, the `SCA` receives an `ABORT` signal from some subnet before getting commitment from all subnets, it will mark the transaction as `ExecAborted` and each subnet is  notified (through a cross-msg) that it may revert/unlock their input state without performing changes to the local state.

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
	Cid    cid.Cid 
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
	Inputs map[cid.Cid]LockedState
}
```

## Collateral and slashing
> WIP. This is just a placeholder for this section. The content included is not final. Follow all design updates [here](https://hackmd.io/HpxNIaacTn2_t6jaDs9RcQ)

When validators join a subnets, they need to provide enough collateral to have validating rights and in order for the subnet to stake over the `CollateralThreshold` required to activate the subnet. The amount of collateral required needs to be enough to make misbehaviors economically irrational for subnet validators. Collateral works as follows: 
- When a subnet is spawned, subnet founders determine the `gasRate` they want to initially support in their subnet. This parameter determines the "load" the child subnet expects to impose in the parent, and according to it the parent sets the `CollateralThreshold` for the subnet. The collateral is also a metric of the _"skin in the game"_ subnet validators have in the subnet. Subnet validators are allowed to add more collateral than the `CollateralThreshold` to signal users their "trustworthiness". However, the only requirement imposed by HC for a subnet to be `Active` (i.e. with the ability to commit checkpoints and interact with the rest of the network) is for the collateral to be over the `CollateralThreshold`.
- Through the operation of the subnet, the `CollateralThreshold` may change according to the `CurrGasRate` reported by the subnet to the parent (through the commitment of checkpoints), and the `MisbehaviorsLevels`, a measure of the number of successful fault proofs for the child subnet committed in the parent, requiring validators to update their collateral accordingly. 

### Detectable misbehaviors
In the following table we specify a list of detectable misbehaviors that we envisions users to be able to report through the commitment of fault proofs, along with the `impact` of the attack. This `impact` parameter is used to determine the amount from the collateral slashed due to the reported misbehavior.

| Misbehavior         | Impact     | Description | Fault Proof |
|--------------|-----------|------------|------------|
| (R4.1) Agreement equivocation               |1|  Deviation on consensus (votes on consensus, checks PoS-based, etc.) | Block checks |
| (R4.2) Invalid state transition             |2| Consensus reaches valid blocks with an invalid state transition   | State replay  |

- __Agreement equivocation__: A malicious majority in a subnet can deviate from the consensus algorithm and propagate as valid a block that should have been considered invalid if the protocol was followed successfully. Agreement equivocations may arise, for instance, in blocks that do not pass all block checks (e.g. blocks are not mined in a different epoch, the block does not includes the right ticket, the block is not signed by the right leader, etc.); if the block doesn't include the right votes in a BFT-like consensus, etc.
To report an agreement equivocation, users need to submit to the parent's SCA the chain of blocks including the equivocated block, and the valid chain replacing the invalid block with a valid one. The SCA perfoms syntactic checks over the inputs and runs the `equivocation_check` function in the corresponding actor of the subnet actor to perform deeper consensus-specific checks. If any of these checks fail, the collateral of the subnet is slashed. The function `equivocation_check` is a mandatory function in the subent actor interface that implements all the consensus-specific checks required to detect agreement equivocations.
Thus, if an agreement equivocation is detected in epoch `n`, a user looking to report the misbehavior needs to report the chain of the latest `n-finality` including the equivocated block, and the valid chain of `n-finality` blocks to the parent SCA. For BFT-like protocols, it may suffice to report the latest block where the equivocation arises, while for sync protocols like Nakamoto consensus --without a clear metric of finality and where long-lasting forks may appear-- reporting agreement equivocations may be impossible.

> Note: The use of Lurk proofs as native primitives in subnets' consensus can simplify and generalize the reporting and detection of agreement equivocations (to the extent of, potentially, completely removing them)

- __Invalid state transition__: Any malicious majority of a subnet can also push invalid state transitions in a valid block. Malicious validators can include messages in a valid block that trigger unallowed state changes. Invalid state transitions are a general misbehavior that may impact HC-specific proccesses like the commitment of checkpoints, or the result of atomic executions.
In order to report an invalid state transition in a subnet, users need to submit to the parent SCA the chain of blocks from the closest valid committed checkpoint to the misbehavior, to the block where the invalid state transition happens. The parent SCA replays every state change in the reported chain and verifies that, indeed, an invalid state transition happened in the reported block. If the misbehaviors is reported successfully, the collateral for the subnet is correspondingly slashed.
Thus, if an invalid state transition happens at block `n`, and the latest committed checkpoint was at block `n-x`, a user looking to report the misbheavior needes to submit to the SCA of the parent the chain of `x` blocks from `n-x` to `n` so the state can be replayed and the invalid state transition checked.
>Note: Along with the checkpoint at `n-x` a snapshot of the state at `n-x` may also need to be provided to enable the whole state of the subnet (for every contract) to be replayed.

## Cross-net routing gas price
> WIP. This is just a placeholder for this section. The content included is not final. Follow all design updates [here](https://hackmd.io/HpxNIaacTn2_t6jaDs9RcQ)

Cross-net messages from a source subnet, `sn_src`, to some other subnet in the hierarchy,`sn_dest`, need to be provided with enough gas for the message to be executed and routeed successfully by every subnet in the path `Path(sn_src, sn_dest)`. Cross-net messages within a subnet are treated as any other message, their execution triggers some state chain that costs certain amoun of gas in the subnet, `gas_cost_sn`. The main difference for cross-net message is that this execution and state change may translate into the propagation of the message to the next subnet in the path. However, for a user to be able to provide the message with enough gas, it needs to have a sense of the cost of execution in each subnet in the path.

To improve the UX and make as predictable as possible this gas estimation, I propose for subnet to publish basic parameters of their gas model when they are spawn: 
- `gas_model_type` (if based in miner tipping, EIP1559-like, etc.)
- `curr_base_fee` (if any)
- etc.

With this information, cross-net message will include an array of `gas_limit` amount that the message wants to dedicate to each subnet in the hop. Subnets in the path won't be able to charge over the specified `gas_limit` for the subnet. When a cross-net reaches a subnet for which `gas_limit` is insufficient, it fails and an error message and the outstanding gas is propagated back to the source.

If a subnet wants to change the parameters of its gas model, it'll need to spawn a new subnet and migrate their traffic there. This prevents subnets from being able to manipulate their gas model and charge different gas costs from the ones publically advertised and harming messages (e.g. forcing gas messages to run out of gas). Ideally, these public gas model parameters used to predict the total gas of a message as a cross-net message traverse a subnet can be extracted from the general crypto-econ model CEL is working on for rootnets (and that will be extrapolated as a configurable general model for subnets).