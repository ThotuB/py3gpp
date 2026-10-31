function [sym, ind] = gen_srs(cfg)
    carrier = nrCarrierConfig;
    carrier.SubcarrierSpacing = cfg.SubcarrierSpacing;
    carrier.NSizeGrid = cfg.NSizeGrid;
    carrier.NStartGrid = cfg.NStartGrid;
    carrier.NSlot = cfg.NSlot;

    srs = nrSRSConfig;
    srs.NumSRSPorts = cfg.NumSRSPorts;
    srs.NumSRSSymbols = cfg.NumSRSSymbols;
    srs.SymbolStart = cfg.SymbolStart;
    srs.CSRS = cfg.CSRS;
    srs.BSRS = cfg.BSRS;
    srs.KTC = cfg.KTC;
    srs.KBarTC = cfg.KBarTC;
    srs.CyclicShift = cfg.CyclicShift;
    srs.FrequencyStart = cfg.FrequencyStart;
    srs.NRRC = cfg.NRRC;
    if iscell(cfg.SRSPeriod)
        srs.SRSPeriod = cell2mat(cfg.SRSPeriod);
    else
        srs.SRSPeriod = cfg.SRSPeriod;
    end

    sym = nrSRS(carrier, srs);
    ind = nrSRSIndices(carrier, srs);
end
