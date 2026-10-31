function ind = gen_pucchindices(cfg)
    carrier = nrCarrierConfig;
    carrier.SubcarrierSpacing = cfg.SubcarrierSpacing;
    carrier.NSizeGrid = cfg.NSizeGrid;
    carrier.NStartGrid = cfg.NStartGrid;
    carrier.NSlot = cfg.NSlot;

    switch cfg.Format
        case 0
            pucch = nrPUCCH0Config;
        case 1
            pucch = nrPUCCH1Config;
        otherwise
            pucch = nrPUCCH2Config;
    end

    pucch.SymbolAllocation = toVec(cfg.SymbolAllocation);
    pucch.PRBSet = toVec(cfg.PRBSet);
    pucch.FrequencyHopping = cfg.FrequencyHopping;
    pucch.SecondHopStartPRB = cfg.SecondHopStartPRB;

    if cfg.Format == 0 || cfg.Format == 1
        pucch.GroupHopping = cfg.GroupHopping;
        pucch.HoppingID = cfg.HoppingID;
        pucch.InitialCyclicShift = cfg.InitialCyclicShift;
    end
    if cfg.Format == 1
        pucch.OCCI = cfg.OCCI;
    end
    if cfg.Format == 2
        pucch.NID = cfg.NID;
        pucch.RNTI = cfg.RNTI;
    end

    ind = nrPUCCHIndices(carrier, pucch);
end

function v = toVec(x)
    if iscell(x)
        v = cell2mat(x);
    else
        v = x;
    end
end
