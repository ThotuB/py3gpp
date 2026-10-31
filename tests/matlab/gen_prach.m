function [sym, ind, nfft, sampleRate] = gen_prach(cfg)
    carrier = nrCarrierConfig;
    carrier.SubcarrierSpacing = cfg.CarrierSubcarrierSpacing;
    carrier.NSizeGrid = cfg.NSizeGrid;
    carrier.NStartGrid = cfg.NStartGrid;

    prach = nrPRACHConfig;
    prach.FrequencyRange = cfg.FrequencyRange;
    prach.DuplexMode = cfg.DuplexMode;
    prach.ConfigurationIndex = cfg.ConfigurationIndex;
    prach.SequenceIndex = cfg.SequenceIndex;
    prach.PreambleIndex = cfg.PreambleIndex;
    prach.RestrictedSet = cfg.RestrictedSet;
    prach.ZeroCorrelationZone = cfg.ZeroCorrelationZone;
    prach.NPRACHSlot = cfg.NPRACHSlot;
    prach.RBOffset = cfg.RBOffset;
    prach.FrequencyStart = cfg.FrequencyStart;
    prach.FrequencyIndex = cfg.FrequencyIndex;

    sym = nrPRACH(carrier, prach);
    ind = nrPRACHIndices(carrier, prach);
    ofdmInfo = nrPRACHOFDMInfo(carrier, prach);
    nfft = ofdmInfo.Nfft;
    sampleRate = ofdmInfo.SampleRate;
end
