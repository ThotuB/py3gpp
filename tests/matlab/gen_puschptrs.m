function [sym, ind] = gen_puschptrs(cfg)
    carrier = nrCarrierConfig;
    carrier.SubcarrierSpacing = cfg.SubcarrierSpacing;
    carrier.NSizeGrid = cfg.NSizeGrid;
    carrier.NStartGrid = cfg.NStartGrid;
    carrier.NSlot = cfg.NSlot;

    pusch = nrPUSCHConfig;
    pusch.NSizeBWP = [];
    pusch.NStartBWP = [];
    pusch.PRBSet = toVec(cfg.PRBSet);
    pusch.SymbolAllocation = toVec(cfg.SymbolAllocation);
    pusch.RNTI = cfg.RNTI;
    pusch.DMRS.DMRSTypeAPosition = cfg.DMRSTypeAPosition;
    pusch.DMRS.DMRSAdditionalPosition = cfg.DMRSAdditionalPosition;
    pusch.EnablePTRS = cfg.EnablePTRS;
    pusch.PTRS.TimeDensity = cfg.PTRSTimeDensity;
    pusch.PTRS.FrequencyDensity = cfg.PTRSFrequencyDensity;
    pusch.PTRS.REOffset = cfg.PTRSREOffset;

    sym = nrPUSCHPTRS(carrier, pusch);
    ind = nrPUSCHPTRSIndices(carrier, pusch);
end

function v = toVec(x)
    if iscell(x)
        v = cell2mat(x);
    else
        v = x;
    end
end
