### *****************************************************************************************
### Usage:
###
### cmsRun topplusdmanaEDMntuples_cfg.py maxEvts=N sample="mySample/sample.root" version="71" outputLabel="myoutput"
###
### Default values for the options are set:
### maxEvts     = -1
### sample      = 'file:/scratch/decosa/ttDM/testSample/tlbsm_53x_v3_mc_10_1_qPV.root'
### outputLabel = 'analysisTTDM.root'
### *****************************************************************************************
import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as opts



options = opts.VarParsing ('analysis')

options.register('maxEvts',
                 -1,# default value: process all events
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.int,
                 'Number of events to process')

options.register('sample',
#                 'file:/afs/cern.ch/user/d/decosa/public/forTTDMteam/patTuple_tlbsm_train_tlbsm_71x_v1.root',
                 'file:/afs/cern.ch/user/d/decosa/public/forTTDMteam/tlbsm_53x_v3_mc_10_1_qPV.root',
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.string,
                 'Sample to analyze')

options.register('version',
                 '53',
                 #'71',
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.string,
                 'ntuple version (53 or 71)')

options.register('outputLabel',
                 'analysisTTDM.root',
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.string,
                 'Output label')

options.parseArguments()


process = cms.Process("ttDManalysisEDMNtuples")

process.load("FWCore.MessageService.MessageLogger_cfi")
### Output Report
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
### Number of maximum events to process
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvts) )
### Source file
process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
        options.sample
        )
)


### Selected leptons and jets
process.skimmedPatMuons = cms.EDFilter(
    "PATMuonSelector",
    src = cms.InputTag("selectedPatMuons"),
    cut = cms.string("pt > 30 && abs(eta) < 2.4")
    )

process.skimmedPatElectrons = cms.EDFilter(
    "PATElectronSelector",
    src = cms.InputTag("selectedPatElectrons"),
    cut = cms.string("pt > 30 && abs(eta) < 2.5")
    )

if options.version=="53" :
    jetLabel="goodPatJetsPFlow"
elif options.version=="71" :
    jetLabel="goodPatJets"
process.skimmedPatJets = cms.EDFilter(
    "CandViewSelector",
    src = cms.InputTag(jetLabel),
#    src = cms.InputTag("goodPatJetsPFlow"), # 53x
#    src = cms.InputTag("goodPatJets"), # 71x    
    cut = cms.string("pt > 25 && abs(eta) < 4.")
    )


### Asking for at least 2 jets satisfying the selection above 
process.jetFilter = cms.EDFilter("CandViewCountFilter",
    src = cms.InputTag("skimmedPatJets"),
    minNumber = cms.uint32(2),
    filter = cms.bool(True)
)

process.muonUserData = cms.EDProducer(
    'MuonUserData',
    muonLabel = cms.InputTag("skimmedPatMuons"),
    pv        = cms.InputTag("goodOfflinePrimaryVertices")
)

from PhysicsTools.CandAlgos.EventShapeVars_cff import *
process.eventShapePFVars = pfEventShapeVars.clone()
process.eventShapePFVars.src = cms.InputTag("particleFlow")

process.eventShapePFJetVars = pfEventShapeVars.clone()
process.eventShapePFJetVars.src = cms.InputTag("skimmedPatJets")

process.centrality = cms.EDProducer("CentralityUserData",
   src = cms.InputTag("skimmedPatJets")
)                                    

### Including ntuplizer 
process.load("ttbarDM.TopPlusDMAna.topplusdmedmNtuples_cff")

### definition of Analysis sequence
process.analysisPath = cms.Path(
    process.skimmedPatElectrons +
    process.skimmedPatMuons +
    process.skimmedPatJets +
    process.eventShapePFVars +
    process.eventShapePFJetVars +
    process.centrality
)

#process.analysisPath+=process.jetFilter
process.analysisPath+=process.muonUserData
process.analysisPath+=process.genPart
process.analysisPath+=process.muons
process.analysisPath+=process.electrons
process.analysisPath+=process.jets

### Creating the filter path to use in order to select events
process.filterPath = cms.Path(
    process.jetFilter
    )


process.edmNtuplesOut.SelectEvents = cms.untracked.PSet(
    SelectEvents = cms.vstring('filterPath')
    )

process.fullPath = cms.Schedule(
    process.analysisPath,
    process.filterPath
    )

process.endPath = cms.EndPath(process.edmNtuplesOut)

## process.outpath = cms.Schedule(
##     process.analysisPath,
##     process.endPath
##     )