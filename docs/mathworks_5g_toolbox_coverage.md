# MathWorks 5G Toolbox — py3gpp Coverage

Function/class inventory crawled from the MathWorks 5G Toolbox documentation (`mathworks.com/help/5g/`), cross-referenced against this repo's current source tree (`py3gpp/`, post category-reorganization). Only these 5 top-level doc categories are in scope: **Downlink Channels**, **Uplink Channels**, **Physical Layer Subcomponents**, **Signal Reception and Recovery**, **Link-Level Simulation**. Excluded as out of scope (Simulink blocks, hardware/RF, AI training objects, code-gen, not plain signal-processing functions): Get Started, System-Level Simulation, RF Simulation, Test and Measurement, AI for 5G NR, 6G Exploration Library, Code Generation and Deployment.

Sub-groupings below (H4 headers) mirror the exact bold group labels MathWorks uses on each page (e.g. "CRC Operations", "Physical Broadcast Channel"). Where a page presents its functions as one flat list with no such labels, it's kept as a single table.

**Summary: 62 of 136 unique functions/classes implemented (~46%).** Uplink is a complete gap (0 of 48). PUCCH/PRACH families are entirely unimplemented; PDCCH/DCI has channel coding, modulation, and non-interleaved resource mapping, but not search-space candidate hashing (see Notable gaps). Status is matched by exact function/class name existing under `py3gpp/` — files are now grouped by category, so several related functions typically live together in one merged module (e.g. `nrBCH`/`nrBCHDecode` both live in `dl/ch/trs/bch.py`). A function marked ❌ may still be partially covered inline inside another file (noted where relevant), but has no standalone implementation.

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
| `nrCSIRS` | Generate CSI-RS symbols | ❌ |
| `nrCSIRSIndices` | Generate CSI-RS resource element indices | ❌ |
| `nrCSIRSConfig` | CSI-RS configuration parameters | ❌ |
| `nrCSIReportConfig` | CSI reporting configuration parameters | ❌ |

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

**Entirely unimplemented — py3gpp has no uplink support at all.**

### Uplink Physical Signals

#### PUSCH Demodulation Reference Signal

| Function | Description | Status |
|---|---|---|
| `nrPUSCHDMRS` | Generate PUSCH DM-RS symbols | ❌ |
| `nrPUSCHDMRSIndices` | Generate PUSCH DM-RS indices | ❌ |
| `nrPUSCHDMRSConfig` | PUSCH DM-RS configuration parameters | ❌ |

#### PUSCH Phase Tracking Reference Signal

| Function | Description | Status |
|---|---|---|
| `nrPUSCHPTRS` | Generate PUSCH PT-RS symbols | ❌ |
| `nrPUSCHPTRSIndices` | Generate PUSCH PT-RS Indices | ❌ |
| `nrPUSCHPTRSConfig` | PUSCH PT-RS configuration parameters | ❌ |

#### Sounding Reference Signal

| Function | Description | Status |
|---|---|---|
| `nrSRS` | Generate uplink SRS symbols | ❌ |
| `nrSRSIndices` | Generate uplink SRS resource element indices | ❌ |
| `nrSRSConfig` | SRS configuration parameters | ❌ |

### Uplink Physical Channels

#### Physical Uplink Shared Channel

| Function | Description | Status |
|---|---|---|
| `nrPUSCH` | Generate PUSCH modulation symbols | ❌ |
| `nrPUSCHIndices` | Generate PUSCH resource element indices | ❌ |
| `nrPUSCHConfig` | PUSCH configuration parameters | ❌ |
| `nrPUSCHDecode` | Decode PUSCH modulation symbols | ❌ |
| `nrPUSCHCodebook` | Generate PUSCH precoding matrix | ❌ |
| `nrPUSCHScramble` | Perform PUSCH scrambling | ❌ |
| `nrPUSCHDescramble` | Perform PUSCH descrambling | ❌ |
| `nrPUSCHPRBS` | Generate PUSCH scrambling sequence | ❌ |
| `nrPUSCHDMRS` | Generate PUSCH DM-RS symbols | ❌ |
| `nrPUSCHDMRSIndices` | Generate PUSCH DM-RS indices | ❌ |
| `nrPUSCHDMRSConfig` | PUSCH DM-RS configuration parameters | ❌ |
| `nrPUSCHPTRS` | Generate PUSCH PT-RS symbols | ❌ |
| `nrPUSCHPTRSIndices` | Generate PUSCH PT-RS Indices | ❌ |
| `nrPUSCHPTRSConfig` | PUSCH PT-RS configuration parameters | ❌ |

#### Physical Uplink Control Channel

| Function | Description | Status |
|---|---|---|
| `nrPUCCH0` | Generate PUCCH format 0 modulation symbols | ❌ |
| `nrPUCCH1` | Generate PUCCH format 1 modulation symbols | ❌ |
| `nrPUCCH2` | Generate PUCCH format 2 modulation symbols | ❌ |
| `nrPUCCH3` | Generate PUCCH format 3 modulation symbols | ❌ |
| `nrPUCCH4` | Generate PUCCH format 4 modulation symbols | ❌ |
| `nrPUCCHHoppingInfo` | Get PUCCH hopping information | ❌ |
| `nrPUCCHPRBS` | Generate PUCCH scrambling sequence | ❌ |
| `nrPUCCH0Config` | PUCCH format 0 configuration parameters | ❌ |
| `nrPUCCH1Config` | PUCCH format 1 configuration parameters | ❌ |
| `nrPUCCH2Config` | PUCCH format 2 configuration parameters | ❌ |
| `nrPUCCH3Config` | PUCCH format 3 configuration parameters | ❌ |
| `nrPUCCH4Config` | PUCCH format 4 configuration parameters | ❌ |
| `nrPUCCH` | Generate PUCCH modulation symbols | ❌ |
| `nrPUCCHIndices` | Generate PUCCH resource element indices | ❌ |
| `nrPUCCHDMRS` | Generate PUCCH DM-RS symbols | ❌ |
| `nrPUCCHDMRSIndices` | Generate PUCCH DM-RS resource element indices | ❌ |
| `nrPUCCHDecode` | Decode PUCCH modulation symbols | ❌ |

#### Physical Random Access Channel

| Function | Description | Status |
|---|---|---|
| `nrPRACH` | Generate PRACH symbols | ❌ |
| `nrPRACHIndices` | Generate PRACH resource element indices | ❌ |
| `nrPRACHConfig` | PRACH configuration parameters | ❌ |
| `nrPRACHGrid` | Generate PRACH resource grid | ❌ |
| `nrPRACHOFDMModulate` | Generate PRACH OFDM modulated waveform | ❌ |
| `nrPRACHOFDMInfo` | Get PRACH OFDM information | ❌ |
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
| `nrULSCHInfo` | Get uplink shared channel (UL-SCH) information | ❌ |
| `nrULSCHMultiplex` | Perform UL-SCH data and control multiplexing | ❌ |
| `nrULSCHDemultiplex` | Perform UL-SCH data and control demultiplexing | ❌ |

### Uplink Control Information

_No sub-grouping on this page — flat function list._

| Function | Description | Status |
|---|---|---|
| `nrUCIEncode` | Encode uplink control information (UCI) | ❌ |
| `nrUCIDecode` | Decode uplink control information (UCI) | ❌ |

### Uplink OFDM Modulation

_No sub-grouping on this page — flat function list._

| Function | Description | Status |
|---|---|---|
| `nrOFDMModulate` | Generate OFDM modulated waveform | ✅ `dl/ofdm.py` (shared, not UL-specific) |
| `nrOFDMDemodulate` | Demodulate OFDM waveform | ✅ `dl/ofdm.py` (shared) |
| `nrOFDMInfo` | Get OFDM information | ✅ `dl/ofdm.py` (shared) |
| `nrPRACHOFDMModulate` | Generate PRACH OFDM modulated waveform | ❌ |
| `nrPRACHOFDMInfo` | Get PRACH OFDM information | ❌ |
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
| `nrRateMatchPolar` | Rate matching for Polar encoded data | ✅ `plc/trs/polar.py` |
| `nrRateRecoverPolar` | Recover rate matched Polar data | ✅ `plc/trs/polar.py` |

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
| `nrLowPAPRS` | Generate low peak-to-average power ratio (low-PAPR) sequence | ❌ |
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

- **Uplink: nothing exists.** No PUSCH, PUCCH, PRACH, SRS, UL-SCH, or UCI support.
- **PDCCH/DCI: channel coding, modulation, and non-interleaved resource mapping only** (`nrDCIEncode`/`nrDCIDecode`, `nrPDCCH`/`nrPDCCHDecode`/`nrPDCCHPRBS`, `nrPDCCHConfig`/`nrCORESETConfig`/`nrSearchSpaceConfig`, `nrPDCCHResources`). Still deferred: interleaved CCE-to-REG mapping (`nrPDCCHResources` raises `NotImplementedError` for `CCEREGMapping="interleaved"`) and search-space candidate hashing per TS 38.213 §10.1 (`nrPDCCHSpace`) — low confidence in exact formula recall for both, and no bundled MATLAB reference data to validate against.
- **No channel models** (CDL/TDL/HST) — only path loss is covered.
- **No perfect channel/timing estimation** — only the "practical" (blind) estimators exist, useful for BER/ideal-case benchmarking.
- `nrPBCHDecode` (physical-channel-level PBCH LLR demod) has no standalone equivalent — only transport-level `nrBCHDecode` exists.
