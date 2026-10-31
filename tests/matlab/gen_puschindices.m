function ind = gen_puschindices(cfg)
    carrier = nrCarrierConfig;
    carrier.SubcarrierSpacing = double(cfg.SubcarrierSpacing);
    carrier.NSizeGrid = double(cfg.NSizeGrid);
    carrier.NStartGrid = double(cfg.NStartGrid);
    carrier.NSlot = double(cfg.NSlot);

    pusch = nrPUSCHConfig;
    pusch.NSizeBWP = [];
    pusch.NStartBWP = [];
    pusch.PRBSet = toVec(cfg.PRBSet);
    pusch.SymbolAllocation = toVec(cfg.SymbolAllocation);
    pusch.DMRS.DMRSTypeAPosition = double(cfg.DMRSTypeAPosition);
    pusch.DMRS.DMRSAdditionalPosition = double(cfg.DMRSAdditionalPosition);
    pusch.DMRS.DMRSConfigurationType = double(cfg.DMRSConfigurationType);

    ind = nrPUSCHIndices(carrier, pusch);
end

function v = toVec(x)
    if iscell(x)
        v = double(cell2mat(x));
    else
        v = double(x);
    end
end
