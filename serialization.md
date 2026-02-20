# Nash Serialisation Protocol
## First Principles
Nash is a **prediction market trading engine**, and as such, must **maintain absolute determinism** to ensure market integrity, resolve disputes fairly, as well as facilitate future audits or studies. \

## Articles to be serialised/deserialised
  - Trading instrument data:
    - Instrument ID
    - Mutex linkages 
  - Account balances, outstanding orders and positions
  - UBI Arbitrage engine balances and position (no margin is requried as the running strategy is strictly delta-neutral)

## Serialisation Method
- Serialise Order Class:
  - Account-ID Mapping
  -
