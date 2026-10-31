function ind = gen_pdschindices(cfg)
    carrier = nrCarrierConfig;
    carrier.SubcarrierSpacing = double(cfg.SubcarrierSpacing);
    carrier.NSizeGrid = double(cfg.NSizeGrid);
    carrier.NStartGrid = double(cfg.NStartGrid);
    carrier.NSlot = double(cfg.NSlot);

    pdsch = nrPDSCHConfig;
    pdsch.NSizeBWP = [];
    pdsch.NStartBWP = [];
    pdsch.PRBSet = toVec(cfg.PRBSet);
    pdsch.SymbolAllocation = toVec(cfg.SymbolAllocation);
    pdsch.DMRS.DMRSTypeAPosition = double(cfg.DMRSTypeAPosition);
    pdsch.DMRS.DMRSAdditionalPosition = double(cfg.DMRSAdditionalPosition);
    pdsch.DMRS.DMRSConfigurationType = double(cfg.DMRSConfigurationType);

    ind = nrPDSCHIndices(carrier, pdsch);
end

function v = toVec(x)
    if iscell(x)
        v = double(cell2mat(x));
    else
        v = double(x);
    end
end
