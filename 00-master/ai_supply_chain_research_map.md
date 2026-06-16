# AI Supply Chain: Investment Map & Research Framework

A working document for systematically identifying and evaluating AI infrastructure investments. Organized bottom-up because per the Aschenbrenner thesis, the binding constraint is power and physical infrastructure, not the headline names.

**How to use this:** Treat each layer as a watchlist. For each name, run the per-stock framework at the bottom. Mark your conviction (✗ / ? / ✓✓ / ✓✓✓) and revisit quarterly.

---

## Layer 1 — Power Generation

The most under-appreciated bottleneck. AI training clusters are siting decisions, not just chip decisions.

### Regulated utilities (data-center geographic exposure)
- **Dominion Energy (D)** — Virginia / Loudoun County, the densest data center market in the world
- **American Electric Power (AEP)** — Ohio, Texas, mid-Atlantic data center corridors
- **Duke Energy (DUK)** — Carolinas, Florida
- **Southern Company (SO)** — Georgia (Vogtle nuclear); large data center pipeline
- **NextEra Energy (NEE)** — renewables + Florida utility
- **Entergy (ETR)** — Mississippi/Louisiana, Meta data center exposure
- **PPL Corp (PPL)** — Pennsylvania, Kentucky
- **Xcel Energy (XEL)** — Colorado, Minnesota

### Independent Power Producers (IPPs)
- **Vistra (VST)** — Texas + acquired Energy Harbor (nuclear)
- **Constellation Energy (CEG)** — largest US nuclear fleet; Microsoft Three Mile Island restart deal
- **Talen Energy (TLN)** — Susquehanna nuclear + AWS data center campus deal
- **NRG Energy (NRG)** — Texas, retail + generation

### Nuclear-specific
- **Cameco (CCJ)** — uranium mining
- **Uranium Energy (UEC)** — US uranium
- **Centrus Energy (LEU)** — HALEU enrichment (needed for SMRs)
- **BWX Technologies (BWXT)** — nuclear components, naval reactors
- **NuScale Power (SMR)** — small modular reactors
- **Oklo (OKLO)** — microreactors, Sam Altman-backed
- **NANO Nuclear (NNE)** — microreactor development

### Natural gas E&P (powering gas turbines for data centers)
- **EQT Corp (EQT)** — largest US gas producer, Appalachian
- **Range Resources (RRC)** — Appalachian
- **Antero Resources (AR)** — Appalachian
- **Coterra Energy (CTRA)** — Permian + Marcellus
- **Expand Energy (EXE)** — formerly Chesapeake, gas-focused

### Distributed / on-site power
- **Bloom Energy (BE)** — solid-oxide fuel cells; Aschenbrenner's largest disclosed long
- **Plug Power (PLUG)** — hydrogen fuel cells
- **Cummins (CMI)** — backup generators, gas turbines
- **Generac (GNRC)** — backup power, distributed generation
- **GE Vernova (GEV)** — gas turbines (huge backlog), wind, grid
- **Solaris Energy Infrastructure (SEI)** — mobile gas-turbine fleets, >2 GW contracted to data-center counterparties (added 2026-06-12, SALP 13F)
- **Power Solutions International (PSIX)** — natural-gas gensets for data centers, Weichai-controlled (added 2026-06-12, SALP 13F)
- **Babcock & Wilcox (BW)** — boiler/steam-turbine islands for behind-the-meter gas power; Applied Digital anchor (added 2026-06-12, SALP 13F)
- **ProPetro Holding (PUMP)** — Permian frac + PROPWR mobile power pivot, ~240 MW contracted (added 2026-06-12, SALP 13F)

### Solar & renewables equipment (behind-the-meter DC power)
- **Nextracker (NXT)** — solar trackers for utility-scale + behind-the-meter data-center power

---
- **T1 Energy (TE)** — US solar module/cell mfg (fka FREYR); AI link prospective only — thesis-adjacent (added 2026-06-12, SALP 13F)

## Layer 2 — Grid & Power Equipment

The transformer shortage is real. Lead times for large power transformers have stretched 2-3+ years.

- **GE Vernova (GEV)** — gas turbines, transformers, grid software
- **Eaton (ETN)** — electrical equipment, data center power distribution
- **Schneider Electric (SBGSY)** — data center power, prefab DC modules
- **ABB Ltd (ABBNY)** — electrification, transformers
- **Hitachi Energy (HTHIY)** — grid transformers
- **Hubbell (HUBB)** — electrical components
- **Quanta Services (PWR)** — electric grid construction
- **MasTec (MTZ)** — infrastructure construction
- **Powell Industries (POWL)** — switchgear, electrical infrastructure
- **nVent Electric (NVT)** — electrical connections & enclosures
- **Atkore (ATKR)** — electrical conduit & cable

---

## Layer 3 — Data Center Construction, REITs & Cooling

- **Digital Realty Trust (DLR)** — colo/wholesale data center REIT
- **Equinix (EQIX)** — interconnection-heavy REIT
- **Iron Mountain (IRM)** — storage REIT pivoting to data centers
- **Vertiv Holdings (VRT)** — data center cooling & power infrastructure (THE pure-play)
- **Comfort Systems USA (FIX)** — mechanical contractor, heavy DC exposure
- **EMCOR Group (EME)** — electrical/mechanical contractor
- **Modine Manufacturing (MOD)** — liquid cooling for DCs
- **AAON (AAON)** — data-center-specific HVAC + liquid-cooling coils; smaller play vs VRT/MOD
- **Carrier Global (CARR)** — HVAC, cooling
- **Trane Technologies (TT)** — HVAC, cooling
- **Johnson Controls (JCI)** — HVAC, building systems

---

## Layer 4 — Semiconductor Equipment & Materials

The capital equipment that enables every AI chip.

### Equipment
- **ASML (ASML)** — EUV lithography monopoly
- **Applied Materials (AMAT)** — deposition, etch, inspection
- **Lam Research (LRCX)** — etch, deposition (memory exposure)
- **KLA Corp (KLAC)** — process control / inspection
- **Tokyo Electron (TOELY)** — Japanese equipment giant
- **Teradyne (TER)** — semiconductor test
- **Onto Innovation (ONTO)** — metrology
- **Camtek (CAMT)** — inspection, advanced packaging
- **Kulicke & Soffa (KLIC)** — packaging equipment
- **BE Semiconductor (BESIY)** — hybrid bonding & die-attach; the enabling tool for HBM4 / advanced packaging (Dutch FPI, US ADR)

### Test & measurement
- **Keysight Technologies (KEYS)** — electronic test equipment for chips, optical, 800G/1.6T networking, PCIe Gen6
- **FormFactor (FORM)** — probe cards for wafer sort; rising HBM / known-good-die test intensity

### Materials & consumables
- **Entegris (ENTG)** — specialty materials
- **MKS Instruments (MKSI)** — vacuum, photonics
- **Photronics (PLAB)** — photomasks
- **Ultra Clean Holdings (UCTT)** — equipment subsystems
- **Advanced Energy (AEIS)** — precision power-delivery subsystems for etch/deposition tools + data-center power

### PCB / substrates
- **TTM Technologies (TTMI)** — high-layer-count PCBs for AI servers, networking switches, defense

### EDA & IP
- **Cadence Design Systems (CDNS)** — EDA software
- **Synopsys (SNPS)** — EDA software, IP
- **Arm Holdings (ARM)** — CPU IP licensing

---

## Layer 5 — Fabs & Foundries

- **TSMC (TSM)** — leading-edge foundry, ~90%+ of AI accelerator wafers
- **Intel (INTC)** — IDM trying to become foundry; Aschenbrenner long via calls
- **GlobalFoundries (GFS)** — mature node specialty
- **Tower Semiconductor (TSEM)** — analog/RF/specialty, in Aschenbrenner portfolio
- **United Microelectronics (UMC)** — mature node Taiwan foundry

---

## Layer 6 — AI Compute Silicon

### GPUs / merchant accelerators
- **NVIDIA (NVDA)** — the incumbent, ~80% AI training market share
- **AMD (AMD)** — MI300/MI350 series, growing inference share
- **Intel (INTC)** — Gaudi accelerators (weaker), but CPU host still relevant

### Custom silicon / ASIC designers
- **Broadcom (AVGO)** — Google TPU + Meta MTIA partner; biggest custom AI play
- **Marvell Technology (MRVL)** — AWS Trainium/Inferentia, custom ASICs, electro-optics
- **Astera Labs (ALAB)** — connectivity ICs (retimers, smart cables)

### Power management silicon
- **Monolithic Power Systems (MPWR)** — voltage regulators and power modules for AI accelerator boards
- **onsemi (ON)** — EliteSiC + PowerTrench + GaN; named in NVIDIA 800VDC AI-datacenter power ecosystem; AI-DC revenue >2x YoY but a small minority (~8%) of a cyclical auto/industrial core
- **Navitas Semiconductor (NVTS)** — GaN/SiC power ICs; design-in for 800VDC data-center power architecture (speculative)

### Programmable logic
- **Lattice Semiconductor (LSCC)** — low-power FPGAs for server platform management / control plane

### Memory (HBM is the bottleneck)
- **Micron (MU)** — HBM3E, HBM4 ramping
- **Rambus (RMBS)** — memory interface chips (RCD/MRDIMM clock drivers) + DDR5/HBM IP licensing; direct memory-bottleneck leverage
- **SanDisk (SNDK)** — NAND/storage spun from WD
- **SK Hynix** — HBM leader (Korea-listed, ADR limited)
- **Samsung** — Korea-listed

### Analog, mixed-signal & embedded (diversified)
*Added 2026-06-15 to close the SMH coverage gap (rule: scored the 8 SMH holdings absent from the watchlist). These are broad-line analog/embedded franchises whose cores are auto/industrial/handset; AI-datacenter content is a real but minority growth sleeve. Their AI-Thesis "directness" (rule 12) is moderate-to-low — the AI-Thesis category, not the Value metric, carries conversion probability (rule 13 division-of-labor).*
- **Texas Instruments (TXN)** — analog + embedded; ~6-7% datacenter (power/signal chain) growing ~90% YoY off a megafab buildout; core is industrial/auto/personal-electronics
- **Analog Devices (ADI)** — signal chain + high-density power (Empower acq.) + optical signal integrity; ~11-12% datacenter, the most AI-levered of the diversified analog group
- **NXP Semiconductors (NXPI)** — auto/industrial/IoT; edge-AI (Kinara NPUs) not hyperscale-buildout; ~0-5% genuine AI-DC exposure
- **Microchip (MCHP)** — MCU/analog/FPGA; Data Center Solutions unit (PCIe switches/retimers, NVMe controllers) ~8% of revenue; deep cyclical recovery
- **STMicroelectronics (STM)** — analog + SiC/GaN power + MCU; NVIDIA 800VDC collaboration, datacenter guided >$1B for 2027; foreign filer (20-F/6-K), deep cyclical trough

### RF front-end & application processors
*Added 2026-06-15 (SMH gap). Handset/connectivity-centric; AI exposure is edge/on-device or immaterial, not hyperscale infrastructure.*
- **Qualcomm (QCOM)** — handset SoC + licensing; on-device/edge AI embedded in SoCs; data-center push (AI200/AI250) is an unproven forward option; Apple modem revenue cliff
- **Skyworks (SWKS)** — RF front-end, ~60% Apple concentration; AI-DC content immaterial; pending Qorvo merger under FTC review

---

## Layer 7 — Optical, Networking & Interconnect

Bandwidth is becoming as important as compute. 800G → 1.6T transitions are massive revenue events.

### Optical components & transceivers
- **Coherent (COHR)** — optical components, transceivers
- **Lumentum (LITE)** — optical, lasers
- **Fabrinet (FN)** — contract manufacturer for Nvidia, Cisco optics
- **Applied Optoelectronics (AAOI)** — optical, datacenter exposure
- **POET Technologies (POET)** — photonics integration (speculative)

### Networking systems
- **Arista Networks (ANET)** — high-end DC switching; big Microsoft/Meta customer
- **Cisco (CSCO)** — networking incumbent
- **Juniper Networks (JNPR)** — HPE acquisition closed
- **Ciena (CIEN)** — optical transport systems

### Connectivity ASICs
- **Credo Technology (CRDO)** — Active Electrical Cables (AECs), line cards, SerDes IP for GPU-to-GPU interconnect

### Cabling & physical layer
- **Amphenol (APH)** — connectors, cables
- **TE Connectivity (TEL)** — connectors
- **Corning (GLW)** — optical fiber

---

## Layer 8 — Servers, Systems & Liquid Cooling

### Server OEMs & systems
- **Super Micro Computer (SMCI)** — AI server OEM (read the audit risks carefully)
- **Dell Technologies (DELL)** — enterprise + AI server growth
- **HP Enterprise (HPE)** — Cray, AI servers, Juniper integration
- **Vertiv (VRT)** — already noted; liquid cooling tailwind
- **Modine Manufacturing (MOD)** — already noted

### Contract manufacturing / ODMs
- **Flex Ltd (FLEX)** — AI server, power, and thermal infrastructure manufacturing; CPI spin-off pending

### Storage infrastructure
- **Everpure (P, fka Pure Storage/PSTG, renamed ~May 2026)** — all-flash arrays (FlashBlade) for AI training data pipelines
- **Seagate Technology (STX)** — nearline mass-capacity HDD for AI data lakes; HAMR ramp tightening supply

---

## Layer 9 — Compute-as-a-Service

### Hyperscalers (public-cloud AI revenue)
- **Microsoft (MSFT)** — Azure + OpenAI partnership
- **Alphabet (GOOGL)** — GCP + DeepMind + TPUs
- **Amazon (AMZN)** — AWS + Anthropic stake + Trainium
- **Meta Platforms (META)** — internal AI + capex monster
- **Oracle (ORCL)** — surprise AI cloud winner, OCI

### Neoclouds (AI-native cloud providers)
- **CoreWeave (CRWV)** — biggest pure-play AI cloud
- **Nebius Group (NBIS)** — former Yandex pieces, EU-based GPU cloud
- **Applied Digital (APLD)** — HPC hosting + crypto pivot
- **WhiteFiber (WYFI)** — Bit Digital AI-infra spinout, NC-1 campus + Montreal colo (added 2026-06-12, SALP 13F)
- **SharonAI Holdings (SHAZ)** — de-SPAC GPU cloud, 132 MW secured / ~2 MW live; severe risk flags (added 2026-06-12, SALP 13F)

### Bitcoin miners pivoting to AI hosting
The thesis here: stranded power contracts + interconnect rights + cheap land = call option on AI capacity.

- **Core Scientific (CORZ)** — biggest HPC pivot, CoreWeave hosting deal
- **IREN Limited (IREN)** — Australian, growing AI hosting
- **Cipher Mining (CIFR)** — Texas, growing AI ambitions
- **CleanSpark (CLSK)** — mining-focused, less AI pivot
- **BitDeer (BTDR)** — Singapore-listed equivalent, mining + AI
- **Hut 8 (HUT)** — Canadian, HPC ambitions
- **Keel Infrastructure (KEEL, fka Bitfarms/BITF until 2026-04-06)** — full HPC/AI pivot, exited new BTC mining investment
- **Riot Platforms (RIOT)** — Texas mining giant
- **TeraWulf (WULF)** — nuclear-powered mining + HPC

---
- **HIVE Digital Technologies (HIVE)** — hydro-powered miner (Canada/Sweden/Paraguay), BUZZ HPC AI pivot (added 2026-06-12, SALP 13F)

## Layer 10 — Models, Software & Applications

Most foundation model labs are private (OpenAI, Anthropic, xAI, Mistral). Public exposure is mostly via hyperscalers above, plus:

### Enterprise AI platforms
- **Palantir (PLTR)** — government/enterprise AI deployment
- **Snowflake (SNOW)** — data layer, AI workloads
- **Databricks** — private but worth tracking IPO
- **ServiceNow (NOW)** — enterprise workflow AI
- **Salesforce (CRM)** — Agentforce, enterprise AI

### AI observability & infrastructure software
- **Datadog (DDOG)** — cloud monitoring and observability; LLM Observability product for AI workloads

### AI cybersecurity
- **CrowdStrike (CRWD)** — endpoint security using AI; protects AI infrastructure attack surface

### AI data layer
- **MongoDB (MDB)** — document database with Atlas Vector Search for RAG / AI applications

### AI-powered automation
- **UiPath (PATH)** — robotic process automation + agentic AI capabilities

### AI-native vertical applications
- **Tempus AI (TEM)** — AI-native precision-medicine data + diagnostics platform

---

## Per-Stock Research Framework

For each name on your watchlist, answer these. Skip none.

### 1. Position in the chain
- What layer does this sit at?
- Is the role unique or commoditized?
- Who do they sell to? (Customer list)
- What % revenue is AI-related vs. legacy?

### 2. Customer concentration
- Top 3 customers as % of revenue (10-K, segment disclosures)
- How dependent on Microsoft / Meta / Google / Amazon capex?
- What's the substitution risk if a customer in-houses?

### 3. Pricing power
- Are prices rising, flat, or falling?
- Backlog growth and lead times — are they widening?
- Gross margin trend over last 8 quarters

### 4. Capital intensity & FCF
- Capex/revenue ratio
- FCF margin and trend
- Is this a capex-funded growth story or self-funding?

### 5. Moat
- IP (patents, process know-how)
- Scale (cost advantage from volume)
- Switching costs (customer integration)
- Network effects (rare in hardware, present in software)
- Regulatory / geographic (utilities)

### 6. Balance sheet
- Net debt / EBITDA
- Interest coverage
- Maturity wall
- Liquidity runway if growth pauses

### 7. Valuation framework
- What's the bull case multiple if AI capex continues 3-5 years?
- What's the bear case multiple if hyperscaler capex pauses?
- What's currently priced in vs. consensus estimates?

### 8. Catalysts (next 4 quarters)
- Earnings dates
- Product launches
- Customer wins likely to be announced
- Capacity additions coming online

### 9. Risks
- What single development breaks the thesis?
- China exposure / export controls
- Cyclical downturn scenarios
- Technology substitution

### 10. Conviction & sizing
- High / medium / low conviction
- Position size as % of portfolio
- Stop-loss or thesis-break trigger

---

## Tracking Framework — What to Monitor Quarterly

### Earnings season checklist
- **Hyperscaler capex guides** (MSFT, GOOGL, AMZN, META, ORCL) — total capex $ and YoY change. This is the leading indicator for the whole stack.
- **NVIDIA earnings** — data center revenue, networking revenue, comments on supply/demand
- **TSMC monthly revenue** + capex guide — high-performance computing segment
- **Vertiv, Eaton, GE Vernova** — backlog, book-to-bill, lead times
- **Utility / IPP earnings** — data center load growth in their service territories

### Between earnings — high-signal sources
- **SEC filings (EDGAR)** — 10-Q, 8-K material announcements, 13F (45 days post quarter)
- **Earnings call transcripts** — read them, not just headlines (look up on Seeking Alpha or company IR)
- **Hyperscaler capex announcements** — press releases for new DC sites, power deals
- **Trade press**:
  - SemiAnalysis (paid, deep technical)
  - The Information (paid, enterprise tech)
  - Reuters / Bloomberg (free + paywalled)
  - Tom's Hardware, AnandTech (technical)
- **Industry events**:
  - GTC (NVIDIA, March)
  - Hot Chips (August)
  - OCP Summit (October)
  - Computex (June)
- **Government data**:
  - EIA monthly electricity reports
  - BLS industrial production
  - ISM manufacturing PMI

### 13F tracking (every Feb / May / Aug / Nov)
Useful to see what others are doing, but treat as confirming evidence, not as a signal to chase:
- Situational Awareness LP
- Stan Druckenmiller (Duquesne)
- Coatue
- Tiger Global
- Whale Wisdom and 13f.info aggregate these

### Government / policy
- CHIPS Act tranches and milestones
- Export controls (BIS notices)
- AI executive orders
- Tax policy on data centers (state-level)
- Permitting reform legislation

---

## Building Your Process

### Weekly (30–60 min)
- Scan earnings releases for any holdings or watchlist names
- Check news for the top 10 hyperscaler capex announcements
- Read 1-2 substantive analyses (SemiAnalysis, blog post, transcript)

### Monthly (2–3 hours)
- Update tracker on every holding: price, fundamentals, thesis still intact?
- Add 2-3 new names from the watchlist for deeper dive
- Review any policy/macro shifts

### Quarterly (1 day)
- Re-run per-stock framework on every position
- Read every earnings call transcript for positions
- Decide on adds / trims / exits
- Update conviction levels

### Annually
- Rewrite your investment thesis from scratch
- Compare to last year's thesis — what did you get right/wrong?
- Update the supply chain map (new entrants, IPOs, M&A)

---

## A Few Principles Worth Internalizing

1. **The further upstream, the less crowded.** Everyone knows NVIDIA. Fewer people understand transformer lead times or HBM allocation dynamics.

2. **Pure plays vs. conglomerates.** A pure play gives you cleaner exposure but more risk. Conglomerates (GE Vernova, Eaton) dilute the AI thesis but de-risk.

3. **The picks-and-shovels meta-trade.** During gold rushes, the shovel sellers often outperform the miners. But the shovels themselves get commoditized over time — watch for the moment when supply catches up.

4. **Capex cycles end.** Hyperscaler capex is at ~$400B+ annually heading into 2026. At some point it normalizes. Have a plan for that.

5. **Inverse the thesis quarterly.** What would prove you wrong? If you can't answer, you don't understand the position.
