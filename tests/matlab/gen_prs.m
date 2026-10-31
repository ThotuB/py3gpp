function [sym, ind] = gen_prs(cfg)
    carrier = nrCarrierConfig;
    carrier.SubcarrierSpacing = cfg.SubcarrierSpacing;
    carrier.NSizeGrid = cfg.NSizeGrid;
    carrier.NStartGrid = cfg.NStartGrid;
    carrier.NSlot = cfg.NSlot;

    prs = nrPRSConfig;
    if ischar(cfg.PRSResourceSetPeriod) || isstring(cfg.PRSResourceSetPeriod)
        prs.PRSResourceSetPeriod = cfg.PRSResourceSetPeriod;
    else
        prs.PRSResourceSetPeriod = toVec(cfg.PRSResourceSetPeriod);
    end
    prs.PRSResourceOffset = toVec(cfg.PRSResourceOffset);
    prs.PRSResourceRepetition = cfg.PRSResourceRepetition;
    prs.PRSResourceTimeGap = cfg.PRSResourceTimeGap;
    prs.MutingPattern1 = toVec(cfg.MutingPattern1);
    prs.MutingBitRepetition = cfg.MutingBitRepetition;
    prs.MutingPattern2 = toVec(cfg.MutingPattern2);
    prs.NumPRSSymbols = toVec(cfg.NumPRSSymbols);
    prs.SymbolStart = toVec(cfg.SymbolStart);
    prs.NumRB = cfg.NumRB;
    prs.RBOffset = cfg.RBOffset;
    prs.CombSize = cfg.CombSize;
    prs.REOffset = toVec(cfg.REOffset);
    prs.NPRSID = toVec(cfg.NPRSID);

    sym = nrPRS(carrier, prs);
    ind = nrPRSIndices(carrier, prs);
end

function v = toVec(x)
    % Python scalars arrive as plain MATLAB doubles; python lists arrive as cell
    % arrays of scalars. Normalize both to a plain numeric row vector.
    if iscell(x)
        v = cell2mat(x);
    else
        v = x;
    end
end
