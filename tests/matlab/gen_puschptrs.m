function [sym, ind] = gen_puschptrs(cfg)
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
    pusch.RNTI = double(cfg.RNTI);
    pusch.DMRS.DMRSTypeAPosition = double(cfg.DMRSTypeAPosition);
    pusch.DMRS.DMRSAdditionalPosition = double(cfg.DMRSAdditionalPosition);
    pusch.EnablePTRS = double(cfg.EnablePTRS);
    pusch.PTRS.TimeDensity = double(cfg.PTRSTimeDensity);
    pusch.PTRS.FrequencyDensity = double(cfg.PTRSFrequencyDensity);
    pusch.PTRS.REOffset = cfg.PTRSREOffset;

    sym = nrPUSCHPTRS(carrier, pusch);
    ind = nrPUSCHPTRSIndices(carrier, pusch);
end

function v = toVec(x)
    if iscell(x)
        v = double(cell2mat(x));
    else
        v = double(x);
    end
end
