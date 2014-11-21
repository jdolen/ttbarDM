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
    'root://cmsxrootd.fnal.gov//store/mc/Phys14DR/BprimeJetToBZ_M800GeV_Tune4C_13TeV-madgraph-tauola/MINIAODSIM/PU20bx25_PHYS14_25_V1-v1/10000/3294933B-DC6B-E411-B853-E0CB4EA0A933.root',
    opts.VarParsing.multiplicity.singleton,
    opts.VarParsing.varType.string,
    'Sample to analyze')

options.register('version',
    #'53',
    '71',
    opts.VarParsing.multiplicity.singleton,
    opts.VarParsing.varType.string,
    'ntuple version (53 or 71)')

options.register('outputLabel',
    'myanalysisTTDM.root',
    opts.VarParsing.multiplicity.singleton,
    opts.VarParsing.varType.string,
    'Output label')

options.register('isData',
    False,
    opts.VarParsing.multiplicity.singleton,
    opts.VarParsing.varType.bool,
    'Is data?')

options.register('miniAOD',
    True,
    opts.VarParsing.multiplicity.singleton,
    opts.VarParsing.varType.bool,
    'miniAOD source')


options.register('LHE',
    True,
    opts.VarParsing.multiplicity.singleton,
    opts.VarParsing.varType.bool,
    'Keep LHEProducts')

options.parseArguments()

if(options.isData):options.LHE = False

###inputTag labels
if(options.miniAOD):
  muLabel  = 'slimmedMuons'
  elLabel  = 'slimmedElectrons'
  jetLabel = 'slimmedJets'
  ak8jetLabel = 'patJetsSlimmedJetsAK8BTagged'
  pvLabel  = 'offlineSlimmedPrimaryVertices'
  particleFlowLabel = 'packedPFCandidates'    
  metLabel = 'slimmedMETs'
else:
  muLabel = 'selectedPatMuons'
  elLabel = 'selectedPatElectrons'
  if options.version=="53" :
    jetLabel="goodPatJetsPFlow"
    ak8jetLabel = ''
  elif options.version=="71" :
    jetLabel="goodPatJets"
    ak8jetLabel="goodPatJetsAK8"
  pvLabel             = "goodOfflinePrimaryVertices"
  particleFlowLabel = "particleFlow"    
  metLabel = 'patMETPF'

triggerResultsLabel = "TriggerResults"
triggerSummaryLabel = "hltTriggerSummaryAOD"
hltMuonFilterLabel       = "hltL3crIsoL1sMu16Eta2p1L1f0L2f16QL3f40QL3crIsoRhoFiltered0p15"
hltPathLabel             = "HLT_Mu8_Ele17_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL"
hltElectronFilterLabel  = "hltL1sL1Mu3p5EG12ORL1MuOpenEG12L3Filtered8"
lheLabel = "source"

process = cms.Process("ttDManalysisEDMNtuples")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.categories.append('HLTrigReport')
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

process.load("PhysicsTools.PatAlgos.producersLayer1.patCandidates_cff")
process.load("Configuration.EventContent.EventContent_cff")
process.load('Configuration.StandardSequences.Geometry_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
from Configuration.AlCa.GlobalTag import GlobalTag as customiseGlobalTag
process.GlobalTag = customiseGlobalTag(process.GlobalTag, globaltag = 'auto:startup_GRun')
process.GlobalTag.connect   = 'frontier://FrontierProd/CMS_COND_31X_GLOBALTAG'
process.GlobalTag.pfnPrefix = cms.untracked.string('frontier://FrontierProd/')
for pset in process.GlobalTag.toGet.value():
  pset.connect = pset.connect.value().replace('frontier://FrontierProd/', 'frontier://FrontierProd/')
#   Fix for multi-run processing:
process.GlobalTag.RefreshEachRun = cms.untracked.bool( False )
process.GlobalTag.ReconnectEachRun = cms.untracked.bool( False )
#process.GlobalTag.globaltag =  'POSTLS172_V3::All'

#for Inclusive Vertex Finder
process.load("RecoBTag/Configuration/RecoBTag_cff")
process.load('RecoVertex/AdaptiveVertexFinder/inclusiveVertexing_cff')
process.inclusiveVertexFinder.tracks = cms.InputTag("unpackedTracksAndVertices")
process.inclusiveVertexFinder.primaryVertices = cms.InputTag("unpackedTracksAndVertices")
process.trackVertexArbitrator.tracks = cms.InputTag("unpackedTracksAndVertices")
process.trackVertexArbitrator.primaryVertices = cms.InputTag("unpackedTracksAndVertices")

#new input for impactParameterTagInfos, softleptons, IVF
process.impactParameterTagInfos.jetTracks = cms.InputTag("jetTracksAssociatorAtVertexSlimmedJetsAK8BTagged")
process.impactParameterTagInfos.primaryVertex = cms.InputTag("unpackedTracksAndVertices")
process.inclusiveVertexFinder.primaryVertices = cms.InputTag("unpackedTracksAndVertices")
process.trackVertexArbitrator.primaryVertices = cms.InputTag("unpackedTracksAndVertices")
process.softPFMuonsTagInfos.primaryVertex = cms.InputTag("unpackedTracksAndVertices")
process.softPFElectronsTagInfos.primaryVertex = cms.InputTag("unpackedTracksAndVertices")
process.softPFMuonsTagInfos.jets = cms.InputTag("patJetsSlimmedJetsAK8BTagged")
process.softPFElectronsTagInfos.jets = cms.InputTag("patJetsSlimmedJetsAK8BTagged") 
process.inclusiveSecondaryVertexFinderTagInfosV2 = process.inclusiveSecondaryVertexFinderTagInfos.clone()
process.inclusiveSecondaryVertexFinderTagInfosV2.trackSelection.qualityClass = cms.string('any')

from PhysicsTools.PatAlgos.tools.jetTools import addJetCollection
addJetCollection(
    process,
    postfix   = "",
    labelName = 'SlimmedJetsAK8BTagged',
    jetSource = cms.InputTag('slimmedJetsAK8'),
    trackSource = cms.InputTag('unpackedTracksAndVertices'),
    pfCandidates = cms.InputTag('packedPFCandidates'), 
    pvSource = cms.InputTag('unpackedTracksAndVertices'), 
    jetCorrections = ('AK4PFchs', cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute']), 'Type-2'),
    btagDiscriminators = [      'combinedSecondaryVertexBJetTags', 'combinedInclusiveSecondaryVertexV2BJetTags'     ]
    ,algo= 'AK', rParam = 0.8
    )

process.patJetFlavourAssociation.jets = "slimmedJetsAK8"
process.patJetFlavourAssociation.rParam = 0.8 

#adjust MC matching
process.patJetGenJetMatchSlimmedJetsAK8BTagged.matched = "slimmedGenJets"
process.patJetPartonMatchSlimmedJetsAK8BTagged.matched = "prunedGenParticles"
process.patJetPartons.particles = "prunedGenParticles"

#adjust PV used for Jet Corrections
process.patJetCorrFactorsSlimmedJetsAK8BTagged.primaryVertices = "unpackedTracksAndVertices"

#adjust JTA cone size 
process.jetTracksAssociatorAtVertexSlimmedJetsAK8BTagged.coneSize = 0.8 

process.load('PhysicsTools.PatAlgos.slimming.unpackedTracksAndVertices_cfi')
process.combinedSecondaryVertex.trackMultiplicityMin = 1 #silly sv, uses un filtered tracks.. i.e. any pt

##
## Jet substructure variables as user floats
##
#process.patJetsSlimmedJetsAK8BTagged.userData.userFloats.src = []
#process.selectedPatJetsSlimmedJetsAK8BTagged.cut = cms.string("pt > 100")
#from RecoJets.Configuration.RecoPFJets_cff import ak8PFJetsCHSPruned, ak8PFJetsCHSFiltered, ak8PFJetsCHSTrimmed
#process.ak8PFJetsCHSPruned   = ak8PFJetsCHSPruned.clone()
#process.ak8PFJetsCHSTrimmed  = ak8PFJetsCHSTrimmed.clone()
#process.ak8PFJetsCHSFiltered = ak8PFJetsCHSFiltered.clone()
#
#process.load("RecoJets.JetProducers.ak8PFJetsCHS_groomingValueMaps_cfi")
#process.ak8PFJetsCHSPrunedLinks.src  = cms.InputTag("slimmedJetsAK8")
#process.ak8PFJetsCHSTrimmedLinks.src  = cms.InputTag("slimmedJetsAK8")
#process.ak8PFJetsCHSFilteredLinks.src = cms.InputTag("slimmedJetsAK8")
#
#process.patJetsSlimmedJetsAK8BTagged.userData.userFloats.src += ['ak8PFJetsCHSPrunedLinks','ak8PFJetsCHSTrimmedLinks','ak8PFJetsCHSFilteredLinks']
#
#process.load('RecoJets.JetProducers.nJettinessAdder_cfi')
#process.NjettinessAK8 = process.Njettiness.clone(src=cms.InputTag("slimmedJetsAK8"),)
#process.NjettinessAK8.cone = cms.double(0.8)
#process.patJetsSlimmedJetsAK8BTagged.userData.userFloats.src += ['NjettinessAK8:tau1','NjettinessAK8:tau2','NjettinessAK8:tau3']

### Selected leptons and jets
process.skimmedPatMuons = cms.EDFilter(
    "PATMuonSelector",
    src = cms.InputTag(muLabel),
    cut = cms.string("pt > 30 && abs(eta) < 2.4")
    )

process.skimmedPatElectrons = cms.EDFilter(
    "PATElectronSelector",
    src = cms.InputTag(elLabel),
    cut = cms.string("pt > 30 && abs(eta) < 2.5")
    )

process.skimmedPatMET = cms.EDFilter(
    "PATMETSelector",
    src = cms.InputTag(metLabel),
    cut = cms.string("")
    )


process.skimmedPatJets = cms.EDFilter(
    "CandViewSelector",
    src = cms.InputTag(jetLabel),
    #    src = cms.InputTag("goodPatJetsPFlow"), # 53x
    #    src = cms.InputTag("goodPatJets"), # 71x    
    cut = cms.string("(( pt > 25 && mass < 20.) || mass > 20. ) && abs(eta) < 4.")
    )

process.skimmedPatJetsAK8 = cms.EDFilter(
    "CandViewSelector",
    src = cms.InputTag(ak8jetLabel),
    #    src = cms.InputTag("goodPatJets"), # 71x    
    cut = cms.string("pt > 25 && abs(eta) < 4.")
    )

### Asking for at least 2 jets satisfying the selection above 
process.jetFilter = cms.EDFilter("CandViewCountFilter",
    src = cms.InputTag("skimmedPatJets"),
    minNumber = cms.uint32(1),
    filter = cms.bool(True)
    )

process.muonUserData = cms.EDProducer(
    'MuonUserData',
    muonLabel = cms.InputTag("skimmedPatMuons"),
    pv        = cms.InputTag(pvLabel),
    #    pv        = cms.InputTag("offlinePrimaryVertices"),
    ### TTRIGGER ###
    triggerResults = cms.InputTag(triggerResultsLabel,"","HLT"),
    triggerSummary = cms.InputTag(triggerSummaryLabel,"","HLT"),
    hltMuonFilter  = cms.InputTag(hltMuonFilterLabel),
    hltPath            = cms.string("HLT_IsoMu40_eta2p1_v11"),
    hlt2reco_deltaRmax = cms.double(0.1),
    #    mainROOTFILEdir    = cms.string("../data/")
    )

process.jetUserData = cms.EDProducer(
    'JetUserData',
    jetLabel  = cms.InputTag("skimmedPatJets"),
    pv        = cms.InputTag(pvLabel),
    ### TTRIGGER ###
    triggerResults = cms.InputTag(triggerResultsLabel,"","HLT"),
    triggerSummary = cms.InputTag(triggerSummaryLabel,"","HLT"),
    hltJetFilter       = cms.InputTag("hltSixCenJet20L1FastJet"),
    hltPath            = cms.string("HLT_QuadJet60_DiJet20_v6"),
    hlt2reco_deltaRmax = cms.double(0.2)
    )

process.electronUserData = cms.EDProducer(
    'ElectronUserData',
    eleLabel = cms.InputTag("skimmedPatElectrons"),
    pv        = cms.InputTag(pvLabel),
    triggerResults = cms.InputTag(triggerResultsLabel),
    triggerSummary = cms.InputTag(triggerSummaryLabel),
    hltElectronFilter  = cms.InputTag(hltElectronFilterLabel),  ##trigger matching code to be fixed!
    hltPath             = cms.string("HLT_Mu8_Ele17_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL")
    )



from PhysicsTools.CandAlgos.EventShapeVars_cff import *
process.eventShapePFVars = pfEventShapeVars.clone()
process.eventShapePFVars.src = cms.InputTag(particleFlowLabel)

process.eventShapePFJetVars = pfEventShapeVars.clone()
process.eventShapePFJetVars.src = cms.InputTag("skimmedPatJets")

process.centrality = cms.EDProducer("CentralityUserData",
    src = cms.InputTag("skimmedPatJets")
    )                                    

### Including ntuplizer 
process.load("ttbarDM.TopPlusDMAna.topplusdmedmNtuples_cff")

process.options.allowUnscheduled = cms.untracked.bool(True)

### definition of Analysis sequence
process.analysisPath = cms.Path(
    process.skimmedPatElectrons +
    process.skimmedPatMuons +
    process.skimmedPatJets +
    process.skimmedPatJetsAK8 +
    process.skimmedPatMET +
    process.eventShapePFVars +
    process.eventShapePFJetVars +
    process.centrality
    )

#process.analysisPath+=process.jetFilter

process.analysisPath+=process.muonUserData
process.analysisPath+=process.jetUserData
process.analysisPath+=process.electronUserData

process.analysisPath+=process.genPart

process.analysisPath+=process.muons

process.analysisPath+=process.electrons
process.analysisPath+=process.jets
process.analysisPath+=process.jetsAK8
process.analysisPath+=process.met

### Creating the filter path to use in order to select events
process.filterPath = cms.Path(
    process.jetFilter
    )

### keep info from LHEProducts if they are stored in PatTuples
if(options.LHE):
  process.LHEUserData = cms.EDProducer("LHEUserData",
      lheLabel = cms.InputTag("source")
      )
  process.analysisPath+=process.LHEUserData
process.edmNtuplesOut.outputCommands+=('keep *_*LHE*_*_*',)
process.edmNtuplesOut.outputCommands+=('keep LHEEventProduct_*_*_*',)

### end LHE products     


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

open('junk.py', 'w').write(process.dumpPython())
