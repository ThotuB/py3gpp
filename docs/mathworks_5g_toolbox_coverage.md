# MathWorks 5G Toolbox — py3gpp Coverage

Function/class inventory crawled from the MathWorks 5G Toolbox documentation (`mathworks.com/help/5g/`), cross-referenced against this repo's current source tree (`py3gpp/`, post category-reorganization). Only these 5 top-level doc categories are in scope: **Downlink Channels**, **Uplink Channels**, **Physical Layer Subcomponents**, **Signal Reception and Recovery**, **Link-Level Simulation**. Excluded as out of scope (Simulink blocks, hardware/RF, AI training objects, code-gen, not plain signal-processing functions): Get Started, System-Level Simulation, RF Simulation, Test and Measurement, AI for 5G NR, 6G Exploration Library, Code Generation and Deployment.

Sub-groupings below (H4 headers) mirror the exact bold group labels MathWorks uses on each page (e.g. "CRC Operations", "Physical Broadcast Channel"). Where a page presents its functions as one flat list with no such labels, it's kept as a single table.

**Summary: 120 of 162 unique functions/classes implemented (~74%).** Uplink now has PUSCH (single-layer, `MappingType="A"` only), `nrULSCHInfo`, PRACH (long preambles, Formats 0-2, unrestricted set, FR1 only), UCI encode/decode (single codeword only), SRS (no hopping/TDM), and PUCCH (all 5 formats' generation, Formats 0/1/2 resource mapping, Formats 1-4 DM-RS, non-interlaced). PDCCH/DCI has channel coding, modulation, and non-interleaved resource mapping, but not search-space candidate hashing; CSI-RS covers only Rows 1-3 of its 18-row resource-mapping table (see Notable gaps). Status is matched by exact function/class name existing under `py3gpp/` — files are now grouped by category, so several related functions typically live together in one merged module (e.g. `nrBCH`/`nrBCHDecode` both live in `dl/ch/trs/bch.py`). A function marked ❌ may still be partially covered inline inside another file (noted where relevant), but has no standalone implementation.

---

## Downlink Channels

### Downlink Physical Signals

#### Synchronization Signals

| Function | Description | Status |
|---|---|---|
| `nrPSS` | Generate PSS symbols | ✅ `dl/sig/ss.py` |
| `nrPSSIndices` | Generate PSS resource element indices | ✅ `dl/sig/ss.py` |
| `nrSSS` | Generate SSS symbols | ✅ `dl/sig/ss.py` |
| `nrSSSIndices` | Generate SSS resource element indices | ✅ `dl/sig/ss.py` |

#### PDSCH Demodulation Reference Signal

| Function | Description | Status |
|---|---|---|
| `nrPDSCHDMRS` | Generate PDSCH DM-RS symbols | ✅ `dl/sig/pdsch_dmrs.py` |
| `nrPDSCHDMRSIndices` | Generate PDSCH DM-RS indices | ✅ `dl/sig/pdsch_dmrs.py` |
| `nrPDSCHDMRSConfig` | PDSCH DM-RS configuration parameters | ✅ `dl/ch/phy/pdsch.py` |

#### PBCH Demodulation Reference Signal

| Function | Description | Status |
|---|---|---|
| `nrPBCHDMRS` | Generate PBCH DM-RS symbols | ✅ `dl/sig/pbch_dmrs.py` |
| `nrPBCHDMRSIndices` | Generate PBCH DM-RS resource element indices | ✅ `dl/sig/pbch_dmrs.py` |

#### Channel State Information Reference Signal

| Function | Description | Status |
|---|---|---|
| `nrCSIRS` | Generate CSI-RS symbols | ✅ `dl/sig/csirs.py` (Rows 1-3 only, see Notable gaps) |
| `nrCSIRSIndices` | Generate CSI-RS resource element indices | ✅ `dl/sig/csirs.py` (Rows 1-3 only, see Notable gaps) |
| `nrCSIRSConfig` | CSI-RS configuration parameters | ✅ `dl/sig/csirs.py` |
| `nrCSIReportConfig` | CSI reporting configuration parameters | ❌ (no CSI feedback/reporting functions exist yet to consume it, see Notable gaps) |

#### PDSCH Phase Tracking Reference Signal

| Function | Description | Status |
|---|---|---|
| `nrPDSCHPTRS` | Generate PDSCH PT-RS symbols | ✅ `dl/sig/pdsch_ptrs.py` |
| `nrPDSCHPTRSIndices` | Generate PDSCH PT-RS Indices | ✅ `dl/sig/pdsch_ptrs.py` |
| `nrPDSCHPTRSConfig` | PDSCH PT-RS configuration parameters | ✅ `dl/ch/phy/pdsch.py` |

#### Positioning Reference Signal

| Function | Description | Status |
|---|---|---|
| `nrPRSConfig` | PRS configuration parameters | ❌ |
| `nrPRS` | Generate PRS symbols | ❌ |
| `nrPRSIndices` | Generate PRS resource element indices | ❌ |

#### Carrier Configuration

| Function | Description | Status |
|---|---|---|
| `nrCarrierConfig` | Carrier configuration parameters | ✅ `dl/ofdm.py` |
| `nrResourceGrid` | Generate empty carrier slot resource grid | ✅ `dl/ofdm.py` |

### Downlink Physical Channels

#### Physical Broadcast Channel

| Function | Description | Status |
|---|---|---|
| `nrPBCH` | Generate PBCH modulation symbols | ✅ `dl/ch/phy/pbch.py` |
| `nrPBCHIndices` | Generate PBCH resource element indices | ✅ `dl/ch/phy/pbch.py` |
| `nrPBCHPRBS` | Generate PBCH scrambling sequence | ✅ `dl/ch/phy/pbch.py` |
| `nrPBCHDecode` | Decode PBCH modulation symbols | ❌ (py3gpp only has transport-level `nrBCHDecode`) |

#### Physical Downlink Shared Channel

| Function | Description | Status |
|---|---|---|
| `nrPDSCH` | Generate PDSCH modulation symbols | ✅ `dl/ch/phy/pdsch.py` |
| `nrPDSCHIndices` | Generate PDSCH resource element indices | ✅ `dl/ch/phy/pdsch.py` |
| `nrPDSCHConfig` | PDSCH configuration parameters | ✅ `dl/ch/phy/pdsch.py` |
| `nrPDSCHPrecode` | Precoding for PDSCH PRG bundling | ❌ |
| `nrPRGInfo` | Precoding resource block group information | ❌ |
| `nrPDSCHDecode` | Decode PDSCH modulation symbols | ✅ `dl/ch/phy/pdsch.py` |
| `nrPDSCHReservedConfig` | PDSCH reserved PRB configuration parameters | ❌ |
| `nrPDSCHPRBS` | Generate PDSCH scrambling sequence | ❌ (scrambling likely inlined in `dl/ch/phy/pdsch.py`) |
| `nrPDSCHDMRS` | Generate PDSCH DM-RS symbols | ✅ `dl/sig/pdsch_dmrs.py` |
| `nrPDSCHDMRSIndices` | Generate PDSCH DM-RS indices | ✅ `dl/sig/pdsch_dmrs.py` |
| `nrPDSCHDMRSConfig` | PDSCH DM-RS configuration parameters | ✅ `dl/ch/phy/pdsch.py` |
| `nrPDSCHPTRS` | Generate PDSCH PT-RS symbols | ✅ `dl/sig/pdsch_ptrs.py` |
| `nrPDSCHPTRSIndices` | Generate PDSCH PT-RS Indices | ✅ `dl/sig/pdsch_ptrs.py` |
| `nrPDSCHPTRSConfig` | PDSCH PT-RS configuration parameters | ✅ `dl/ch/phy/pdsch.py` |

#### Physical Downlink Control Channel

| Function | Description | Status |
|---|---|---|
| `nrPDCCH` | Generate PDCCH modulation symbols | ✅ `dl/ch/phy/pdcch.py` |
| `nrPDCCHResources` | Generate PDCCH and PDCCH DM-RS resources | ✅ `dl/ch/phy/pdcch.py` (non-interleaved CCE-to-REG mapping only, see Notable gaps) |
| `nrPDCCHSpace` | Generate PDCCH resources for all candidates and aggregation levels | ❌ (search-space candidate hashing deferred, see Notable gaps) |
| `nrPDCCHConfig` | PDCCH configuration parameters | ✅ `dl/ch/phy/pdcch.py` |
| `nrCORESETConfig` | Control resource set (CORESET) configuration parameters | ✅ `dl/ch/phy/pdcch.py` |
| `nrSearchSpaceConfig` | Search space set configuration parameters | ✅ `dl/ch/phy/pdcch.py` |
| `nrPDCCHDecode` | Decode PDCCH modulation symbols | ✅ `dl/ch/phy/pdcch.py` |
| `nrPDCCHPRBS` | Generate PDCCH scrambling sequence | ✅ `dl/ch/phy/pdcch.py` |

#### Carrier Configuration

| Function | Description | Status |
|---|---|---|
| `nrCarrierConfig` | Carrier configuration parameters | ✅ `dl/ofdm.py` |
| `nrResourceGrid` | Generate empty carrier slot resource grid | ✅ `dl/ofdm.py` |

### Downlink Transport Channels

#### Broadcast Channel

| Function | Description | Status |
|---|---|---|
| `nrBCH` | Broadcast channel (BCH) encoding | ✅ `dl/ch/trs/bch.py` |
| `nrBCHDecode` | Broadcast channel (BCH) decoding | ✅ `dl/ch/trs/bch.py` |

#### Downlink Shared Channel

| Function | Description | Status |
|---|---|---|
| `nrDLSCH` | Apply DL-SCH encoder processing chain | ❌ (steps exist individually: CRC/LDPC/rate-match in `plc/trs/`, no single pipeline wrapper) |
| `nrDLSCHDecoder` | Apply DL-SCH decoder processing chain | ❌ (same — no wrapper) |
| `nrDLSCHInfo` | Get downlink shared channel (DL-SCH) information | ✅ `dl/ch/trs/dlsch.py` |

### Downlink Control Information

_No sub-grouping on this page — flat function list._

| Function | Description | Status |
|---|---|---|
| `nrDCIEncode` | Encode downlink control information (DCI) | ✅ `dl/dci.py` |
| `nrDCIDecode` | Decode downlink control information (DCI) | ✅ `dl/dci.py` |

### Downlink OFDM Modulation

_No sub-grouping on this page — flat function list._

| Function | Description | Status |
|---|---|---|
| `nrOFDMModulate` | Generate OFDM modulated waveform | ✅ `dl/ofdm.py` |
| `nrOFDMDemodulate` | Demodulate OFDM waveform | ✅ `dl/ofdm.py` |
| `nrOFDMInfo` | Get OFDM information | ✅ `dl/ofdm.py` |
| `nrResourceGrid` | Generate empty carrier slot resource grid | ✅ `dl/ofdm.py` |

---

## Uplink Channels

**PUSCH is implemented (single-layer, `MappingType="A"`, `DMRSConfigurationType=1` only — the same real limitations `nrPDSCH`/`nrPDSCHDMRS` have today). PUCCH (all 5 formats' generation; Formats 0/1/2 resource mapping; Formats 1-4 DM-RS), PRACH, SRS, and UCI are implemented with scoped limitations (see Notable gaps); only `nrPUSCHPTRS` and PUCCH/PUSCH PT-RS-adjacent features remain entirely unimplemented.**

### Uplink Physical Signals

#### PUSCH Demodulation Reference Signal

| Function | Description | Status |
|---|---|---|
| `nrPUSCHDMRS` | Generate PUSCH DM-RS symbols | ✅ `ul/sig/pusch_dmrs.py` |
| `nrPUSCHDMRSIndices` | Generate PUSCH DM-RS indices | ✅ `ul/sig/pusch_dmrs.py` |
| `nrPUSCHDMRSConfig` | PUSCH DM-RS configuration parameters | ✅ `ul/ch/phy/pusch.py` |

#### PUSCH Phase Tracking Reference Signal

| Function | Description | Status |
|---|---|---|
| `nrPUSCHPTRS` | Generate PUSCH PT-RS symbols | ❌ |
| `nrPUSCHPTRSIndices` | Generate PUSCH PT-RS Indices | ❌ |
| `nrPUSCHPTRSConfig` | PUSCH PT-RS configuration parameters | ❌ |

#### Sounding Reference Signal

| Function | Description | Status |
|---|---|---|
| `nrSRS` | Generate uplink SRS symbols | ✅ `ul/sig/srs.py` (no frequency/comb/cyclic-shift hopping, no 8-port TDM, see Notable gaps) |
| `nrSRSIndices` | Generate uplink SRS resource element indices | ✅ `ul/sig/srs.py` (same scope as `nrSRS`) |
| `nrSRSConfig` | SRS configuration parameters | ✅ `ul/sig/srs.py` |

### Uplink Physical Channels

#### Physical Uplink Shared Channel

| Function | Description | Status |
|---|---|---|
| `nrPUSCH` | Generate PUSCH modulation symbols | ✅ `ul/ch/phy/pusch.py` (single-layer only; optional transform precoding via `nrTransformPrecode`) |
| `nrPUSCHIndices` | Generate PUSCH resource element indices | ✅ `ul/ch/phy/pusch.py` |
| `nrPUSCHConfig` | PUSCH configuration parameters | ✅ `ul/ch/phy/pusch.py` |
| `nrPUSCHDecode` | Decode PUSCH modulation symbols | ✅ `ul/ch/phy/pusch.py` |
| `nrPUSCHCodebook` | Generate PUSCH precoding matrix | ❌ (MIMO precoding — `nrPUSCH` only supports `nlayers=1` so far) |
| `nrPUSCHScramble` | Perform PUSCH scrambling | ❌ (scrambling inlined into `nrPUSCH`/`nrPUSCHDecode`, matching how PDSCH does it) |
| `nrPUSCHDescramble` | Perform PUSCH descrambling | ❌ (same — inlined) |
| `nrPUSCHPRBS` | Generate PUSCH scrambling sequence | ✅ `ul/ch/phy/pusch.py` |
| `nrPUSCHDMRS` | Generate PUSCH DM-RS symbols | ✅ `ul/sig/pusch_dmrs.py` |
| `nrPUSCHDMRSIndices` | Generate PUSCH DM-RS indices | ✅ `ul/sig/pusch_dmrs.py` |
| `nrPUSCHDMRSConfig` | PUSCH DM-RS configuration parameters | ✅ `ul/ch/phy/pusch.py` |
| `nrPUSCHPTRS` | Generate PUSCH PT-RS symbols | ❌ |
| `nrPUSCHPTRSIndices` | Generate PUSCH PT-RS Indices | ❌ |
| `nrPUSCHPTRSConfig` | PUSCH PT-RS configuration parameters | ❌ |

#### Physical Uplink Control Channel

| Function | Description | Status |
|---|---|---|
| `nrPUCCH0` | Generate PUCCH format 0 modulation symbols | ✅ `ul/ch/phy/pucch.py` (non-interlaced only, see Notable gaps) |
| `nrPUCCH1` | Generate PUCCH format 1 modulation symbols | ✅ `ul/ch/phy/pucch.py` (non-interlaced only, see Notable gaps) |
| `nrPUCCH2` | Generate PUCCH format 2 modulation symbols | ✅ `ul/ch/phy/pucch.py` (non-interlaced only, see Notable gaps) |
| `nrPUCCH3` | Generate PUCCH format 3 modulation symbols | ✅ `ul/ch/phy/pucch.py` (non-interlaced only, see Notable gaps) |
| `nrPUCCH4` | Generate PUCCH format 4 modulation symbols | ✅ `ul/ch/phy/pucch.py` (non-interlaced only, see Notable gaps) |
| `nrPUCCHHoppingInfo` | Get PUCCH hopping information | ✅ `ul/ch/phy/pucch.py` |
| `nrPUCCHPRBS` | Generate PUCCH scrambling sequence | ✅ `ul/ch/phy/pucch.py` |
| `nrPUCCH0Config` | PUCCH format 0 configuration parameters | ✅ `ul/ch/phy/pucch.py` |
| `nrPUCCH1Config` | PUCCH format 1 configuration parameters | ✅ `ul/ch/phy/pucch.py` |
| `nrPUCCH2Config` | PUCCH format 2 configuration parameters | ✅ `ul/ch/phy/pucch.py` |
| `nrPUCCH3Config` | PUCCH format 3 configuration parameters | ✅ `ul/ch/phy/pucch.py` (non-interlaced fields only, see Notable gaps) |
| `nrPUCCH4Config` | PUCCH format 4 configuration parameters | ✅ `ul/ch/phy/pucch.py` (non-interlaced fields only, see Notable gaps) |
| `nrPUCCH` | Generate PUCCH modulation symbols | ❌ (the format-dispatching wrapper itself; use `nrPUCCH0`-`nrPUCCH4` directly, see Notable gaps) |
| `nrPUCCHIndices` | Generate PUCCH resource element indices | ✅ `ul/ch/phy/pucch.py` (Formats 0/1/2 only, non-interlaced, see Notable gaps) |
| `nrPUCCHDMRS` | Generate PUCCH DM-RS symbols | ✅ `ul/ch/phy/pucch.py` (Formats 1-4, non-interlaced, Type 1 low-PAPR DM-RS only, see Notable gaps) |
| `nrPUCCHDMRSIndices` | Generate PUCCH DM-RS resource element indices | ✅ `ul/ch/phy/pucch.py` (Formats 1-4, non-interlaced, see Notable gaps) |
| `nrPUCCHDecode` | Decode PUCCH modulation symbols | ❌ (deferred, see Notable gaps) |

#### Physical Random Access Channel

| Function | Description | Status |
|---|---|---|
| `nrPRACH` | Generate PRACH symbols | ✅ `ul/ch/phy/prach.py` (long preambles, Formats 0/1/2, unrestricted set, FR1 only, see Notable gaps) |
| `nrPRACHIndices` | Generate PRACH resource element indices | ✅ `ul/ch/phy/prach.py` (same scope as `nrPRACH`) |
| `nrPRACHConfig` | PRACH configuration parameters | ✅ `ul/ch/phy/prach.py` |
| `nrPRACHGrid` | Generate PRACH resource grid | ❌ |
| `nrPRACHOFDMModulate` | Generate PRACH OFDM modulated waveform | ❌ (see Notable gaps) |
| `nrPRACHOFDMInfo` | Get PRACH OFDM information | ✅ `ul/ch/phy/prach.py` (Format 0, `StartingSymbol=0` only, see Notable gaps) |
| `nrPRACHDetect` | Detect PRACH transmission | ❌ |

#### Carrier Configuration

| Function | Description | Status |
|---|---|---|
| `nrCarrierConfig` | Carrier configuration parameters | ✅ `dl/ofdm.py` |
| `nrResourceGrid` | Generate empty carrier slot resource grid | ✅ `dl/ofdm.py` |
| `nrIntraCellGuardBandsConfig` | Intracell guard bands configuration parameters | ❌ |

### Uplink Transport Channels

_No sub-grouping on this page — flat function list._

| Function | Description | Status |
|---|---|---|
| `nrULSCH` | Apply UL-SCH encoder processing chain | ❌ |
| `nrULSCHDecoder` | Apply UL-SCH decoder processing chain | ❌ |
| `nrULSCHInfo` | Get uplink shared channel (UL-SCH) information | ✅ `ul/ch/trs/ulsch.py` (thin wrapper reusing `nrDLSCHInfo`'s base-graph/CB-segmentation helpers — shared math per TS 38.212) |
| `nrULSCHMultiplex` | Perform UL-SCH data and control multiplexing | ❌ |
| `nrULSCHDemultiplex` | Perform UL-SCH data and control demultiplexing | ❌ |

### Uplink Control Information

_No sub-grouping on this page — flat function list._

| Function | Description | Status |
|---|---|---|
| `nrUCIEncode` | Encode uplink control information (UCI) | ✅ `ul/ch/trs/uci.py` (single codeword only, Polar path requires nmax 9/10, see Notable gaps) |
| `nrUCIDecode` | Decode uplink control information (UCI) | ✅ `ul/ch/trs/uci.py` (same scope as `nrUCIEncode`) |

### Uplink OFDM Modulation

_No sub-grouping on this page — flat function list._

| Function | Description | Status |
|---|---|---|
| `nrOFDMModulate` | Generate OFDM modulated waveform | ✅ `dl/ofdm.py` (shared, not UL-specific) |
| `nrOFDMDemodulate` | Demodulate OFDM waveform | ✅ `dl/ofdm.py` (shared) |
| `nrOFDMInfo` | Get OFDM information | ✅ `dl/ofdm.py` (shared) |
| `nrPRACHOFDMModulate` | Generate PRACH OFDM modulated waveform | ❌ (see Notable gaps) |
| `nrPRACHOFDMInfo` | Get PRACH OFDM information | ✅ `ul/ch/phy/prach.py` (Format 0, `StartingSymbol=0` only, see Notable gaps) |
| `nrResourceGrid` | Generate empty carrier slot resource grid | ✅ `dl/ofdm.py` (shared) |
| `nrTransformPrecode` | Generate transform precoded symbols | ✅ `plc/sym.py` |
| `nrTransformDeprecode` | Recover transform deprecoded symbols | ✅ `plc/sym.py` |

---

## Physical Layer Subcomponents

### Transport Channel Subcomponents

#### CRC Operations

| Function | Description | Status |
|---|---|---|
| `nrCRCEncode` | CRC encoding | ✅ `plc/trs/crc.py` |
| `nrCRCDecode` | CRC decoding | ✅ `plc/trs/crc.py` |

#### LDPC Processing

| Function | Description | Status |
|---|---|---|
| `nrLDPCEncode` | LDPC encoding | ✅ `plc/trs/ldpc.py` |
| `nrLDPCDecode` | LDPC decoding | ✅ `plc/trs/ldpc.py` |
| `nrRateMatchLDPC` | Rate matching for LDPC encoded data | ✅ `plc/trs/ldpc.py` |
| `nrRateRecoverLDPC` | Recover rate matched LDPC data | ✅ `plc/trs/ldpc.py` |
| `nrCodeBlockSegmentLDPC` | Code block segmentation for LDPC coding | ✅ `plc/trs/ldpc.py` |
| `nrCodeBlockDesegmentLDPC` | Code block desegmentation and CRC decoding | ✅ `plc/trs/ldpc.py` |

#### Polar Coding

| Function | Description | Status |
|---|---|---|
| `nrPolarEncode` | Polar encoding | ✅ `plc/trs/polar.py` |
| `nrPolarDecode` | Polar decoding | ✅ `plc/trs/polar.py` |
| `nrRateMatchPolar` | Rate matching for Polar encoded data | ✅ `plc/trs/polar.py` (repetition only, `N<=E`; puncturing/shortening is `N>E` and not yet implemented; the uplink `ibil` triangular interleaver is now supported) |
| `nrRateRecoverPolar` | Recover rate matched Polar data | ✅ `plc/trs/polar.py` (same scope as `nrRateMatchPolar`) |

#### Reference Functions

| Function | Description | Status |
|---|---|---|
| `nrTBS` | Transport block size | ✅ `plc/trs/ref.py` |
| `nrCQITables` | CQI mapping tables | ❌ |
| `nrPDSCHMCSTables` | PDSCH MCS mapping tables | ✅ `plc/trs/ref.py` |
| `nrPUSCHMCSTables` | PUSCH MCS mapping tables | ❌ |

### Physical Channel and Signal Subcomponents

_No sub-grouping on this page — flat function list (confirmed by re-fetch; unlike its sibling "Transport Channel Subcomponents" page, this one has no bold group labels)._

| Function | Description | Status |
|---|---|---|
| `nrPRBS` | Generate PRBS | ✅ `plc/sym.py` |
| `nrLowPAPRS` | Generate low peak-to-average power ratio (low-PAPR) sequence | ✅ `plc/sym.py` (Type 1 only — TS 38.211 5.2.2; Type 2, the `cinit`-based variant for R16 transform-precoded PUSCH DM-RS/PUCCH 3-4, is unimplemented) |
| `nrSymbolModulate` | Generate modulated symbols | ✅ `plc/sym.py` |
| `nrSymbolDemodulate` | Demodulate and convert symbols to bits | ✅ `plc/sym.py` |
| `nrLayerMap` | Layer mapping of modulated and scrambled codewords | ✅ `plc/sym.py` |
| `nrLayerDemap` | Layer demapping onto scrambled and modulated codewords | ❌ |
| `nrTransformPrecode` | Generate transform precoded symbols | ✅ `plc/sym.py` |
| `nrTransformDeprecode` | Recover transform deprecoded symbols | ✅ `plc/sym.py` |

---

## Signal Reception and Recovery

_No sub-grouping on this page — flat function list (confirmed by re-fetch)._

| Function | Description | Status |
|---|---|---|
| `nrPerfectChannelEstimate` | Perfect channel estimation | ❌ |
| `nrPerfectTimingEstimate` | Perfect timing estimation | ❌ |
| `nrChannelEstimate` | Practical channel estimation | ✅ `rx.py` |
| `nrTimingEstimate` | Practical timing estimation | ✅ `rx.py` |
| `nrEqualizeMMSE` | Minimum mean-squared error (MMSE) equalization | ✅ `rx.py` |
| `nrExtractResources` | Extract resource elements from resource array | ✅ `rx.py` |
| `nrPhaseNoiseEstimate` | Estimate phase-noise-induced CPE | ❌ (only `tests/test_phase_compensation.py` exists, no library implementation) |
| `nrPhaseNoiseCompensate` | Compensate phase-noise-induced CPE | ❌ (same — test exists, no library implementation) |

---

## Link-Level Simulation

_No sub-grouping on this page — flat function list (confirmed by re-fetch)._

| Function | Description | Status |
|---|---|---|
| `nrCDLChannel` | Model CDL MIMO channel | ❌ |
| `nrTDLChannel` | Model TDL MIMO channel model | ❌ |
| `nrHSTChannel` | Model HST MIMO channel | ❌ |
| `nrPathLossConfig` | Path loss configuration parameters | ✅ `rx.py` |
| `nrPathLoss` | Path loss and shadow fading between BS and UE | ✅ `rx.py` |

---

## Notable gaps worth prioritizing

- **Uplink: PUSCH, PRACH (long preambles only), UCI, SRS, PUCCH, and `nrULSCHInfo`.** PUSCH (`ul/ch/phy/pusch.py`) is single-layer, `MappingType="A"`, `DMRSConfigurationType=1` only (same real limitations `nrPDSCH`/`nrPDSCHDMRS` have). `nrPUSCHCodebook` (MIMO precoding) is unimplemented since multi-layer PUSCH isn't supported yet. PRACH (`ul/ch/phy/prach.py`) covers long preambles (Formats 0-2, `L_RA=839`) with the unrestricted cyclic-shift set, FR1 only — verified against a live MATLAB 5G Toolbox session (exact sequence/indices/OFDM-info match for Formats 0-2, plus the full embedded root-sequence and FR1 config tables transcribed directly from the toolbox source, since 3GPP numeric tables aren't copyrightable MathWorks expression). Deferred: Format 3 (5 kHz, fractional slot-duration semantics not yet verified), short preambles (`L_RA=139/571/1151`), restricted sets Type A/B, FR2, `nrPRACHOFDMInfo` beyond Format 0/`StartingSymbol=0` (the general case needs the `getSubframeAdjustment` subframe-straddling logic, which is substantial), and `nrPRACHOFDMModulate`/`nrPRACHGrid`/`nrPRACHDetect` entirely. `nrUCIEncode`/`nrUCIDecode` (`ul/ch/trs/uci.py`) cover repetition/simplex/Reed-Muller (`A=1..11`) and single-codeword Polar (`A=20..359`, verified bit-exact against a live MATLAB session) — along the way, fixed a real pre-existing gap in `nrRateMatchPolar`/`nrRateRecoverPolar` (the uplink-only `ibil` triangular interleaver was previously unimplemented). Deferred: the `A=12..19` 6-bit-CRC range (TS 38.212's own formula always resolves to Polar `nmax=8` there, but this repo's `nrPolarDecode` only supports `nmax` 9 or 10 — a pre-existing limitation, not new), two-codeword segmentation (`A>=1013`, or `A>=360` with `Euci>=1088`), and any `(A, Euci)` combination whose resolved `N` exceeds `Euci` (puncturing/shortening, same pre-existing `nrRateMatchPolar` gap PRACH/DCI already work around). SRS (`ul/sig/srs.py`) covers the single-resource, fixed-bandwidth case — verified bit-exact against two live MATLAB sessions (2-port/comb-2 and 4-port/comb-4, including nonzero `CyclicShift`/`FrequencyStart`/`NRRC`). Deferred: frequency hopping (`BHop<BSRS`, the odd/even-`Nb` `F_b` formula), comb-offset hopping, cyclic-shift hopping, 8-port TDM, Rel-17 partial frequency sounding, SRS positioning, and `GroupSeqHopping` other than `"neither"` — all raise `NotImplementedError`. Along the way, found and fixed a real scope bug: `nrLowPAPRS` had been added during the PRACH work as a narrow `nrLowPAPRS(u, length)` (just the bare Zadoff-Chu formula) — but PRACH actually calls MATLAB's bare `zadoffChuSeq` directly, not `nrLowPAPRS`. The *real* `nrLowPAPRS(u,v,alpha,m)` (now correctly implemented in `plc/sym.py`, Type 1 only) is the richer group/sequence/cyclic-shift generator SRS actually needs. PUCCH (`ul/ch/phy/pucch.py`) covers all 5 symbol-generation functions (`nrPUCCH0`-`nrPUCCH4`, all non-interlaced) plus `nrPUCCHHoppingInfo`/`nrPUCCHPRBS` and their 5 config classes; `nrPUCCHIndices` covers Formats 0/1/2, and `nrPUCCHDMRS`/`nrPUCCHDMRSIndices` cover Formats 1-4 (Format 0 has no DM-RS), all non-interlaced — verified bit-exact against live MATLAB sessions for every generation function and every indices function (9 non-DM-RS configs across all 5 formats plus 8 DM-RS configs across formats 1-4, spanning hopping/no-hopping, odd/even symbol counts, and nonzero `NStartGrid`). This work caught several real bugs: PUCCH1's composite-`nSF` block-wise-spreading phase table isn't a simple DFT matrix (had to transcribe the exact per-`nSF` tables), PUCCH4's blockwise spreading needed `np.repeat` not `np.tile`, the DM-RS format-1 hop split needs the real `ceil`/`floor` formula (not a simplified one, which `nrPUCCHDMRSIndices`' format-1 branch initially got wrong), and — most notably — both `nrPUCCHIndices` and `nrPUCCHDMRSIndices` had a latent carrier/BWP-offset bug (used raw `NStartBWP` instead of `NStartBWP - NStartGrid`) that only a nonzero-`NStartGrid` test case exposed, since every earlier PUCCH test happened to use `NStartGrid=0`; now fixed and covered by a regression test in both. Deferred: `nrPUCCH` (the format-dispatching wrapper — callers should use `nrPUCCH0`-`nrPUCCH4` directly), `nrPUCCHIndices` for formats 3/4 (needs the same DM-RS-symbol-position table now built for `nrPUCCHDMRS`, so this is now a cheap follow-up rather than a real gap), `DMRSUplinkTransformPrecodingR16` (the Rel-16 transform-precoded/Type-2-low-PAPR DM-RS variant for formats 3/4 — needs the Type 2 `nrLowPAPRS`, which doesn't exist yet), `nrPUCCHDecode`, and Rel-16 interlacing (`Interlacing=True`, unlicensed-spectrum RB-set spreading) across every format — all raise `NotImplementedError`. UL-SCH multiplexing/demultiplexing also remains unimplemented.
- **PDCCH/DCI: channel coding, modulation, and non-interleaved resource mapping only** (`nrDCIEncode`/`nrDCIDecode`, `nrPDCCH`/`nrPDCCHDecode`/`nrPDCCHPRBS`, `nrPDCCHConfig`/`nrCORESETConfig`/`nrSearchSpaceConfig`, `nrPDCCHResources`). Still deferred: interleaved CCE-to-REG mapping (`nrPDCCHResources` raises `NotImplementedError` for `CCEREGMapping="interleaved"`) and search-space candidate hashing per TS 38.213 §10.1 (`nrPDCCHSpace`) — low confidence in exact formula recall for both, and no bundled MATLAB reference data to validate against.
- **CSI-RS: Rows 1-3 of 18 only** (`nrCSIRS`/`nrCSIRSIndices`/`nrCSIRSConfig` in `dl/sig/csirs.py`) — 1-port (density `'three'`/`'one'`) and 2-port fd-CDM2. Rows 4-18 (4/8/12/16/24/32-port, CDM4/CDM8, multi-frequency-group patterns) raise `NotImplementedError`: the exact k-offset combinations in TS 38.211 Table 7.4.1.5.3-1 couldn't be verified without a live MATLAB session or the spec text itself (MathWorks docs only cite the table, they don't reproduce it). ZP (zero-power/muted) CSI-RS is also unimplemented. `nrCSIReportConfig` is unimplemented — it's a pure CQI/PMI/RI feedback-reporting parameter container with no consuming function anywhere in this repo (no uplink, no CSI measurement/reporting processing exists at all).
- **No channel models** (CDL/TDL/HST) — only path loss is covered.
- **No perfect channel/timing estimation** — only the "practical" (blind) estimators exist, useful for BER/ideal-case benchmarking.
- `nrPBCHDecode` (physical-channel-level PBCH LLR demod) has no standalone equivalent — only transport-level `nrBCHDecode` exists.
