function [sym, ind] = gen_pucchdmrs(cfg)
    carrier = nrCarrierConfig;
    carrier.SubcarrierSpacing = cfg.SubcarrierSpacing;
    carrier.NSizeGrid = cfg.NSizeGrid;
    carrier.NStartGrid = cfg.NStartGrid;
    carrier.NSlot = cfg.NSlot;

    switch cfg.Format
        case 1
            pucch = nrPUCCH1Config;
        case 2
            pucch = nrPUCCH2Config;
        case 3
            pucch = nrPUCCH3Config;
        otherwise
            pucch = nrPUCCH4Config;
    end

    pucch.SymbolAllocation = toVec(cfg.SymbolAllocation);
    pucch.PRBSet = toVec(cfg.PRBSet);
    pucch.FrequencyHopping = cfg.FrequencyHopping;
    pucch.SecondHopStartPRB = cfg.SecondHopStartPRB;

    if cfg.Format == 1
        pucch.GroupHopping = cfg.GroupHopping;
        pucch.HoppingID = cfg.HoppingID;
        pucch.InitialCyclicShift = cfg.InitialCyclicShift;
        pucch.OCCI = cfg.OCCI;
    elseif cfg.Format == 2
        pucch.NID0 = cfg.NID0;
    else
        pucch.GroupHopping = cfg.GroupHopping;
        pucch.HoppingID = cfg.HoppingID;
        pucch.AdditionalDMRS = cfg.AdditionalDMRS;
        if cfg.Format == 4
            pucch.SpreadingFactor = cfg.SpreadingFactor;
            pucch.OCCI = cfg.OCCI;
        end
    end

    sym = nrPUCCHDMRS(carrier, pucch);
    ind = nrPUCCHDMRSIndices(carrier, pucch);
end

function v = toVec(x)
    if iscell(x)
        v = cell2mat(x);
    else
        v = x;
    end
end
