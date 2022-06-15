# Async Reading Group on Consensus Protocols

We will use this repo to provide short summary of consensus protocols that we read.
We read these papers in the light of applying them to Filecoin's hierarchical consensus root protocol, i.e., top level. Informally the requirements that we look for when reading these papers are, by order of importance (in addition to the usual security properties considered by any consensus protocols):
- scaling to ten thousands nodes
- censorship resistance. This specifically applies to WindowPosts that should be included in the chain 30 minutes after a sector is challenged on-chain.
- relatively low finality. Ideally, checkpoints coming from subnets should be included in the chain within 5 minutes (this may however be too strong of a requirement).
- fairness
- simplicity

# List of papers

## Priority

- [ ] Avalance -> @xuechao2 reading
- [ ] Spacemesh -> @sa8 reading 

## Already read (summary to appear)
- [ ] Algorand
- [ ] ColorDAG
- [ ] Order-Fair Consensus in the Permissionless Setting
- [ ] Ebb and Flow and its follow-ups: 
    - [ ] checkpointed longest-chain (fc21)
    - [ ] accountability gadget (fc22)
- [ ] parallel chain protocols
    - [ ] prism
    - [ ] ledger combiner

## De-prioritized papers
- Hot-stuff -> not scalable enough
- Longest-chain protocols -> too long finality
    - (incl Chia)
- eth 2.0 -> many attacks vector (cf papers by Stanford)
- DAG-based protocols https://dahliamalkhi.github.io/posts/2022/06/dag-bft/
    - not scalable enough