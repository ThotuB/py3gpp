function [dmrsSymbols, dmrsIndices, ptrsSymbols, ptrsIndices] = gen_pdschdmrs(cfg)
    carrier = nrCarrierConfig;
    carrier.SubcarrierSpacing = 120;
    carrier.CyclicPrefix = 'normal';
    carrier.NSizeGrid = 132;
    carrier.NStartGrid = 0;

    % Configure the physical downlink shared channel parameters
    pdsch = nrPDSCHConfig;
    pdsch.NSizeBWP = [];   % Empty implies that the value is equal to NSizeGrid
    pdsch.NStartBWP = [];  % Empty implies that the value is equal to NStartGrid
    pdsch.MappingType = cfg.MappingType; % PDSCH mapping type ('A' or 'B')
    pdsch.DMRS.DMRSTypeAPosition = double(cfg.DMRSTypeAPosition);      % 2 or 3
    pdsch.DMRS.DMRSLength = double(cfg.DMRSLength);             % 1 or 2
    pdsch.DMRS.DMRSAdditionalPosition = double(cfg.DMRSAdditionalPosition); % 0...3
    pdsch.PRBSet = double(vertcat(cfg.PRBSet{:}));   % Allocate the complete carrier
    pdsch.SymbolAllocation = double([cfg.SymbolAllocation{1} cfg.SymbolAllocation{2}]); % Symbol allocation [S L]
    pdsch.DMRS.DMRSConfigurationType = double(cfg.DMRSConfigurationType); % 1 or 2
    pdsch.DMRS.DMRSPortSet = 0;
    pdsch.DMRS.NumCDMGroupsWithoutData = 1; % 1 corresponds to CDM group number 0
    pdsch.DMRS.NIDNSCID = double(cfg.NIDNSCID); % Use empty to set it to NCellID of the carrier
    pdsch.DMRS.NSCID = double(cfg.NSCID);    % 0 or 1
    pdsch.NumLayers = numel(pdsch.DMRS.DMRSPortSet);

    % Generate DM-RS indices
    dmrsSymbols = nrPDSCHDMRS(carrier, pdsch);
    dmrsIndices = nrPDSCHDMRSIndices(carrier, pdsch);

    if (cfg.EnablePTRS)
        pdsch.EnablePTRS = double(cfg.EnablePTRS);
        pdsch.RNTI = 1;
        pdsch.PTRS.TimeDensity = double(cfg.PTRSTimeDensity);
        pdsch.PTRS.FrequencyDensity = double(cfg.PTRSFrequencyDensity); % 2 or 4
        pdsch.PTRS.REOffset = cfg.PTRSREOffset;      % '00', '01', '10', '11'
        pdsch.PTRS.PTRSPortSet = min(pdsch.DMRS.DMRSPortSet);
    end

    ptrsSymbols = nrPDSCHPTRS(carrier, pdsch);
    ptrsIndices = nrPDSCHPTRSIndices(carrier, pdsch);
end

