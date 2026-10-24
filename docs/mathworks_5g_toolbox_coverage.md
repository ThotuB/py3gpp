# MathWorks 5G Toolbox — py3gpp Coverage

Function/class inventory crawled from the MathWorks 5G Toolbox documentation (`mathworks.com/help/5g/`), cross-referenced against this repo's current source tree (`py3gpp/`, post category-reorganization). Only these 5 top-level doc categories are in scope: **Downlink Channels**, **Uplink Channels**, **Physical Layer Subcomponents**, **Signal Reception and Recovery**, **Link-Level Simulation**. Excluded as out of scope (Simulink blocks, hardware/RF, AI training objects, code-gen, not plain signal-processing functions): Get Started, System-Level Simulation, RF Simulation, Test and Measurement, AI for 5G NR, 6G Exploration Library, Code Generation and Deployment.

Sub-groupings below (H4 headers) mirror the exact bold group labels MathWorks uses on each page (e.g. "CRC Operations", "Physical Broadcast Channel"). Where a page presents its functions as one flat list with no such labels, it's kept as a single table.

**Summary: 53 of 136 unique functions/classes implemented (~39%).** Uplink is a complete gap (0 of 48). PDCCH/DCI and PUCCH/PRACH families are entirely unimplemented. Status is matched by exact file name under `py3gpp/` — a function marked ❌ may still be partially covered inline inside another file (noted where relevant), but has no standalone implementation.

---

## Downlink Channels

### Downlink Physical Signals

#### Synchronization Signals

| Function | Description | Status |
|---|---|---|
| `nrPSS` | Generate PSS symbols | ✅ `downlink_physical_signals/` |
| `nrPSSIndices` | Generate PSS resource element indices | ✅ `downlink_physical_signals/` |
| `nrSSS` | Generate SSS symbols | ✅ `downlink_physical_signals/` |
| `nrSSSIndices` | Generate SSS resource element indices | ✅ `downlink_physical_signals/` |

#### PDSCH Demodulation Reference Signal

| Function | Description | Status |
|---|---|---|
| `nrPDSCHDMRS` | Generate PDSCH DM-RS symbols | ✅ `downlink_physical_signals/` |
| `nrPDSCHDMRSIndices` | Generate PDSCH DM-RS indices | ✅ `downlink_physical_signals/` |
| `nrPDSCHDMRSConfig` | PDSCH DM-RS configuration parameters | ✅ `configs/` |

#### PBCH Demodulation Reference Signal

| Function | Description | Status |
|---|---|---|
| `nrPBCHDMRS` | Generate PBCH DM-RS symbols | ✅ `downlink_physical_signals/` |
| `nrPBCHDMRSIndices` | Generate PBCH DM-RS resource element indices | ✅ `downlink_physical_signals/` |

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
| `nrPDSCHPTRS` | Generate PDSCH PT-RS symbols | ✅ `downlink_physical_signals/` |
| `nrPDSCHPTRSIndices` | Generate PDSCH PT-RS Indices | ✅ `downlink_physical_signals/` |
| `nrPDSCHPTRSConfig` | PDSCH PT-RS configuration parameters | ✅ `configs/` |

#### Positioning Reference Signal

| Function | Description | Status |
|---|---|---|
| `nrPRSConfig` | PRS configuration parameters | ❌ |
| `nrPRS` | Generate PRS symbols | ❌ |
| `nrPRSIndices` | Generate PRS resource element indices | ❌ |

#### Carrier Configuration

| Function | Description | Status |
|---|---|---|
| `nrCarrierConfig` | Carrier configuration parameters | ✅ `configs/` |
| `nrResourceGrid` | Generate empty carrier slot resource grid | ✅ `downlink_ofdm_modulation/` |

### Downlink Physical Channels

#### Physical Broadcast Channel

| Function | Description | Status |
|---|---|---|
| `nrPBCH` | Generate PBCH modulation symbols | ✅ `downlink_physical_channels/` |
| `nrPBCHIndices` | Generate PBCH resource element indices | ✅ `downlink_physical_channels/` |
| `nrPBCHPRBS` | Generate PBCH scrambling sequence | ✅ `downlink_physical_channels/` |
| `nrPBCHDecode` | Decode PBCH modulation symbols | ❌ (py3gpp only has transport-level `nrBCHDecode`) |

#### Physical Downlink Shared Channel

| Function | Description | Status |
|---|---|---|
| `nrPDSCH` | Generate PDSCH modulation symbols | ✅ `downlink_physical_channels/` |
| `nrPDSCHIndices` | Generate PDSCH resource element indices | ✅ `downlink_physical_channels/` |
| `nrPDSCHConfig` | PDSCH configuration parameters | ✅ `configs/` |
| `nrPDSCHPrecode` | Precoding for PDSCH PRG bundling | ❌ |
| `nrPRGInfo` | Precoding resource block group information | ❌ |
| `nrPDSCHDecode` | Decode PDSCH modulation symbols | ✅ `downlink_physical_channels/` |
| `nrPDSCHReservedConfig` | PDSCH reserved PRB configuration parameters | ❌ |
| `nrPDSCHPRBS` | Generate PDSCH scrambling sequence | ❌ (scrambling likely inlined in `nrPDSCH.py`) |
| `nrPDSCHDMRS` | Generate PDSCH DM-RS symbols | ✅ `downlink_physical_signals/` |
| `nrPDSCHDMRSIndices` | Generate PDSCH DM-RS indices | ✅ `downlink_physical_signals/` |
| `nrPDSCHDMRSConfig` | PDSCH DM-RS configuration parameters | ✅ `configs/` |
| `nrPDSCHPTRS` | Generate PDSCH PT-RS symbols | ✅ `downlink_physical_signals/` |
| `nrPDSCHPTRSIndices` | Generate PDSCH PT-RS Indices | ✅ `downlink_physical_signals/` |
| `nrPDSCHPTRSConfig` | PDSCH PT-RS configuration parameters | ✅ `configs/` |

#### Physical Downlink Control Channel

| Function | Description | Status |
|---|---|---|
| `nrPDCCH` | Generate PDCCH modulation symbols | ❌ |
| `nrPDCCHResources` | Generate PDCCH and PDCCH DM-RS resources | ❌ |
| `nrPDCCHSpace` | Generate PDCCH resources for all candidates and aggregation levels | ❌ |
| `nrPDCCHConfig` | PDCCH configuration parameters | ❌ |
| `nrCORESETConfig` | Control resource set (CORESET) configuration parameters | ❌ |
| `nrSearchSpaceConfig` | Search space set configuration parameters | ❌ |
| `nrPDCCHDecode` | Decode PDCCH modulation symbols | ❌ |
| `nrPDCCHPRBS` | Generate PDCCH scrambling sequence | ❌ |

#### Carrier Configuration

| Function | Description | Status |
|---|---|---|
| `nrCarrierConfig` | Carrier configuration parameters | ✅ `configs/` |
| `nrResourceGrid` | Generate empty carrier slot resource grid | ✅ `downlink_ofdm_modulation/` |

### Downlink Transport Channels

#### Broadcast Channel

| Function | Description | Status |
|---|---|---|
| `nrBCH` | Broadcast channel (BCH) encoding | ✅ `downlink_transport_channels/` |
| `nrBCHDecode` | Broadcast channel (BCH) decoding | ✅ `downlink_transport_channels/` |

#### Downlink Shared Channel

| Function | Description | Status |
|---|---|---|
| `nrDLSCH` | Apply DL-SCH encoder processing chain | ❌ (steps exist individually: CRC/LDPC/rate-match in `transport_channel_subcomponents/`, no single pipeline wrapper) |
| `nrDLSCHDecoder` | Apply DL-SCH decoder processing chain | ❌ (same — no wrapper) |
| `nrDLSCHInfo` | Get downlink shared channel (DL-SCH) information | ✅ `downlink_transport_channels/` |

### Downlink Control Information

_No sub-grouping on this page — flat function list._

| Function | Description | Status |
|---|---|---|
| `nrDCIEncode` | Encode downlink control information (DCI) | ❌ |
| `nrDCIDecode` | Decode downlink control information (DCI) | ❌ |

### Downlink OFDM Modulation

_No sub-grouping on this page — flat function list._

| Function | Description | Status |
|---|---|---|
| `nrOFDMModulate` | Generate OFDM modulated waveform | ✅ `downlink_ofdm_modulation/` |
| `nrOFDMDemodulate` | Demodulate OFDM waveform | ✅ `downlink_ofdm_modulation/` |
| `nrOFDMInfo` | Get OFDM information | ✅ `downlink_ofdm_modulation/` |
| `nrResourceGrid` | Generate empty carrier slot resource grid | ✅ `downlink_ofdm_modulation/` |

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
| `nrCarrierConfig` | Carrier configuration parameters | ✅ `configs/` |
| `nrResourceGrid` | Generate empty carrier slot resource grid | ✅ `downlink_ofdm_modulation/` |
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
| `nrOFDMModulate` | Generate OFDM modulated waveform | ✅ `downlink_ofdm_modulation/` (shared, not UL-specific) |
| `nrOFDMDemodulate` | Demodulate OFDM waveform | ✅ `downlink_ofdm_modulation/` (shared) |
| `nrOFDMInfo` | Get OFDM information | ✅ `downlink_ofdm_modulation/` (shared) |
| `nrPRACHOFDMModulate` | Generate PRACH OFDM modulated waveform | ❌ |
| `nrPRACHOFDMInfo` | Get PRACH OFDM information | ❌ |
| `nrResourceGrid` | Generate empty carrier slot resource grid | ✅ `downlink_ofdm_modulation/` (shared) |
| `nrTransformPrecode` | Generate transform precoded symbols | ✅ `physical_channel_and_signal_subcomponents/` |
| `nrTransformDeprecode` | Recover transform deprecoded symbols | ✅ `physical_channel_and_signal_subcomponents/` |

---

## Physical Layer Subcomponents

### Transport Channel Subcomponents

#### CRC Operations

| Function | Description | Status |
|---|---|---|
| `nrCRCEncode` | CRC encoding | ✅ `transport_channel_subcomponents/` |
| `nrCRCDecode` | CRC decoding | ✅ `transport_channel_subcomponents/` |

#### LDPC Processing

| Function | Description | Status |
|---|---|---|
| `nrLDPCEncode` | LDPC encoding | ✅ `transport_channel_subcomponents/` |
| `nrLDPCDecode` | LDPC decoding | ✅ `transport_channel_subcomponents/` |
| `nrRateMatchLDPC` | Rate matching for LDPC encoded data | ✅ `transport_channel_subcomponents/` |
| `nrRateRecoverLDPC` | Recover rate matched LDPC data | ✅ `transport_channel_subcomponents/` |
| `nrCodeBlockSegmentLDPC` | Code block segmentation for LDPC coding | ✅ `transport_channel_subcomponents/` |
| `nrCodeBlockDesegmentLDPC` | Code block desegmentation and CRC decoding | ✅ `transport_channel_subcomponents/` |

#### Polar Coding

| Function | Description | Status |
|---|---|---|
| `nrPolarEncode` | Polar encoding | ✅ `transport_channel_subcomponents/` |
| `nrPolarDecode` | Polar decoding | ✅ `transport_channel_subcomponents/` |
| `nrRateMatchPolar` | Rate matching for Polar encoded data | ✅ `transport_channel_subcomponents/` |
| `nrRateRecoverPolar` | Recover rate matched Polar data | ✅ `transport_channel_subcomponents/` |

#### Reference Functions

| Function | Description | Status |
|---|---|---|
| `nrTBS` | Transport block size | ✅ `transport_channel_subcomponents/` |
| `nrCQITables` | CQI mapping tables | ❌ |
| `nrPDSCHMCSTables` | PDSCH MCS mapping tables | ✅ `transport_channel_subcomponents/` |
| `nrPUSCHMCSTables` | PUSCH MCS mapping tables | ❌ |

### Physical Channel and Signal Subcomponents

_No sub-grouping on this page — flat function list (confirmed by re-fetch; unlike its sibling "Transport Channel Subcomponents" page, this one has no bold group labels)._

| Function | Description | Status |
|---|---|---|
| `nrPRBS` | Generate PRBS | ✅ `physical_channel_and_signal_subcomponents/` |
| `nrLowPAPRS` | Generate low peak-to-average power ratio (low-PAPR) sequence | ❌ |
| `nrSymbolModulate` | Generate modulated symbols | ✅ `physical_channel_and_signal_subcomponents/` |
| `nrSymbolDemodulate` | Demodulate and convert symbols to bits | ✅ `physical_channel_and_signal_subcomponents/` |
| `nrLayerMap` | Layer mapping of modulated and scrambled codewords | ✅ `physical_channel_and_signal_subcomponents/` |
| `nrLayerDemap` | Layer demapping onto scrambled and modulated codewords | ❌ |
| `nrTransformPrecode` | Generate transform precoded symbols | ✅ `physical_channel_and_signal_subcomponents/` |
| `nrTransformDeprecode` | Recover transform deprecoded symbols | ✅ `physical_channel_and_signal_subcomponents/` |

---

## Signal Reception and Recovery

_No sub-grouping on this page — flat function list (confirmed by re-fetch)._

| Function | Description | Status |
|---|---|---|
| `nrPerfectChannelEstimate` | Perfect channel estimation | ❌ |
| `nrPerfectTimingEstimate` | Perfect timing estimation | ❌ |
| `nrChannelEstimate` | Practical channel estimation | ✅ `signal_reception_and_recovery/` |
| `nrTimingEstimate` | Practical timing estimation | ✅ `signal_reception_and_recovery/` |
| `nrEqualizeMMSE` | Minimum mean-squared error (MMSE) equalization | ✅ `signal_reception_and_recovery/` |
| `nrExtractResources` | Extract resource elements from resource array | ✅ `signal_reception_and_recovery/` |
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
| `nrPathLossConfig` | Path loss configuration parameters | ✅ `configs/` |
| `nrPathLoss` | Path loss and shadow fading between BS and UE | ✅ `signal_reception_and_recovery/` |

---

## Notable gaps worth prioritizing

- **Uplink: nothing exists.** No PUSCH, PUCCH, PRACH, SRS, UL-SCH, or UCI support.
- **PDCCH/DCI: nothing exists.** No control channel decode path on the downlink side either.
- **No channel models** (CDL/TDL/HST) — only path loss is covered.
- **No perfect channel/timing estimation** — only the "practical" (blind) estimators exist, useful for BER/ideal-case benchmarking.
- `nrPBCHDecode` (physical-channel-level PBCH LLR demod) has no standalone equivalent — only transport-level `nrBCHDecode` exists.
