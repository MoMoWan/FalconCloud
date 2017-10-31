
from collections import defaultdict
from . import trees


class _LedmTreeResourceDict(dict):
    def __missing__(self, key):
        return key

Adapters = "/IoMgmt/Adapters"
CartridgeHistory = "/Supplies/CartridgeHistory.xml"
CIMation = "/DevMgmt/CIMation.xml"
ConsumableConfigCap = "/DevMgmt/ConsumableConfigCap.xml"
ConsumableConfigDyn = "/DevMgmt/ConsumableConfigDyn.xml"
CopyConfigDyn = "/DevMgmt/CopyConfigDyn.xml"
DiscoveryTree = "/DevMgmt/DiscoveryTree.xml"
EICommand = "/DevMgmt/EICommand.xml"
HPSupplyMemory = "/Supplies/HPSupplyMemory.xml"
InternalPrintDyn = "/DevMgmt/InternalPrintDyn.xml"
InternalPrintCap = "/DevMgmt/InternalPrintCap.xml"
ManufacturingConfigDyn = "/DevMgmt/ManufacturingConfigDyn.xml"
ManufacturingConfigCap = "/DevMgmt/ManufacturingConfigCap.xml"
MediaCap = "/DevMgmt/MediaCap.xml"
MediaDyn = "/DevMgmt/MediaDyn.xml"
MediaHandlingCap = "/DevMgmt/MediaHandlingCap.xml"
MediaHandlingDyn = "/DevMgmt/MediaHandlingDyn.xml"
NetAppsDyn = "/DevMgmt/NetAppsDyn.xml"
NetAppsSecureDyn = "/DevMgmt/NetAppsSecureDyn.xml"
PrintConfigCap = "/DevMgmt/PrintConfigCap.xml"
PrintConfigDyn = "/DevMgmt/PrintConfigDyn.xml"
ProductConfigCap = "/DevMgmt/ProductConfigCap.xml"
ProductConfigDyn = "/DevMgmt/ProductConfigDyn.xml"
ProductLogsDyn = "/DevMgmt/ProductLogsDyn.xml"
ProductStatusDyn = "/DevMgmt/ProductStatusDyn.xml"
Wifi = "/IoMgmt/Adapters/Wifi0"
WifiNetworks = "/IoMgmt/Adapters/Wifi0/WifiNetworks"
WifiProfile = "/IoMgmt/Adapters/Wifi0/Profiles/Active"
wifi = "/IoMgmt/Adapters/wifi0"
wifiNetworks = "/IoMgmt/Adapters/wifi0/WifiNetworks"
wifiProfile = "/IoMgmt/Adapters/wifi0/Profiles/Active"
Wifi_Phx = "/IoMgmt/Adapters/wifi0"
WifiNetworks_Phx = "/IoMgmt/Adapters/wifi0/WifiNetworks"
WifiProfile_Phx = "/IoMgmt/Adapters/wifi0/Profiles/Active"

TREES_URI = _LedmTreeResourceDict({
    "Adapters": "/IoMgmt/Adapters",
    "CIMation": "/DevMgmt/CIMation.xml",
    "ConsumableConfigDyn": "/DevMgmt/ConsumableConfigDyn.xml",
    "CopyConfigDyn": "/DevMgmt/CopyConfigDyn.xml",
    "DiscoveryTree": "/DevMgmt/DiscoveryTree.xml",
    "EICommand": "/DevMgmt/EICommand.xml",
    "EIStatusVars": "/DevMgmt/EIStatusVars.xml",
    "InternalPrintDyn": "/DevMgmt/InternalPrintDyn.xml",
    "InternalPrintCap": "/DevMgmt/InternalPrintCap.xml",
    "ManufacturingConfigCap": "/DevMgmt/ManufacturingConfigCap.xml",
    "ManufacturingConfigDyn": "/DevMgmt/ManufacturingConfigDyn.xml",    
    "MediaDyn": "/DevMgmt/MediaDyn.xml",
    "MediaHandlingDyn": "/DevMgmt/MediaHandlingDyn.xml",
    "NetAppsDyn": "/DevMgmt/NetAppsDyn.xml",
    "NetAppsSecureDyn": "/DevMgmt/NetAppsSecureDyn.xml",
    "PrintConfigDyn": "/DevMgmt/PrintConfigDyn.xml",
    "ProductConfigDyn": "/DevMgmt/ProductConfigDyn.xml",
    "ProductLogsDyn": "/DevMgmt/ProductLogsDyn.xml",
    "ProductStatusDyn": "/DevMgmt/ProductStatusDyn.xml",
    "Wifi": "/IoMgmt/Adapters/Wifi0",
    "WifiNetworks" : "/IoMgmt/Adapters/Wifi0/WifiNetworks",
    "WifiProfile" : "/IoMgmt/Adapters/Wifi0/Profiles/Active",
    "wifi": "/IoMgmt/Adapters/wifi0",
    "wifiNetworks" : "/IoMgmt/Adapters/wifi0/WifiNetworks",
    "wifiProfile" : "/IoMgmt/Adapters/wifi0/Profiles/Active"
})


TREES_MFG_PASSWORD = ["ManufacturingConfigDyn", "CIMation", "EICommand"]

TREE_MAPPING_TO_OBJECT = defaultdict(lambda: trees.ledm_tree.LEDMTree,
                                     {
                                         "Adapters": trees.Adapters,
                                         "/IoMgmt/Adapters": trees.Adapters,
                                         "Wifi": trees.Adapters,
										 "wifi": trees.Adapters,

                                         "CIMation": trees.CIMation,
                                         "/DevMgmt/CIMation.xml": trees.CIMation,

                                         "CopyConfigDyn": trees.CopyConfigDyn,
                                         "/DevMgmt/CopyConfigDyn.xml": trees.CopyConfigDyn,

                                         "EICommand": trees.EICommand,
                                         "/DevMgmt/EICommand.xml": trees.EICommand,

                                         "EIStatusVars": trees.EIStatusVars,
                                         "/DevMgmt/EIStatusVars.xml": trees.EIStatusVars,

                                         "InternalPrintDyn": trees.InternalPrintDyn,
                                         "/DevMgmt/InternalPrintDyn.xml": trees.InternalPrintDyn,

                                         "InternalPrintCap": trees.InternalPrintCap,
                                         "/DevMgmt/InternalPrintCap.xml": trees.InternalPrintCap,

                                         "ManufacturingConfigDyn": trees.ManufacturingConfigDyn,
                                         "/DevMgmt/ManufacturingConfigDyn.xml": trees.ManufacturingConfigDyn,

                                         "MediaDyn": trees.MediaDyn,
                                         "/DevMgmt/MediaDyn.xml": trees.MediaDyn,

                                         "NetAppsDyn": trees.NetAppsDyn,
                                         "/DevMgmt/NetAppsDyn.xml": trees.NetAppsDyn,

                                         "NetAppsSecureDyn": trees.NetAppsSecureDyn,
                                         "/DevMgmt/NetAppsSecureDyn.xml": trees.NetAppsSecureDyn,

                                         "MediaHandlingDyn": trees.MediaHandlingDyn,
                                         "/DevMgmt/MediaHandlingDyn.xml": trees.MediaHandlingDyn,

                                         "ProductConfigDyn": trees.ProductConfigDyn,
                                         "/DevMgmt/ProductConfigDyn.xml": trees.ProductConfigDyn,

                                         "ProductLogsDyn": trees.ProductLogsConfigDyn,
                                         "/DevMgmt/ProductLogsDyn.xml": trees.ProductLogsConfigDyn,

                                         "ProductStatusDyn": trees.ProductStatusDyn,
                                         "/DevMgmt/ProductStatusDyn.xml": trees.ProductStatusDyn,

                                         "WifiNetworks" : trees.WifiNetworks,
                                         "/IoMgmt/Adapters/Wifi0/WifiNetworks" : trees.WifiNetworks,
                                         "/IoMgmt/Adapters/wifi0/WifiNetworks": trees.WifiNetworks,

                                         "WifiProfile" : trees.WifiProfile,
                                         "/IoMgmt/Adapters/Wifi0/Profiles/Active" : trees.WifiProfile,
                                         
                                         "wifiNetworks" : trees.WifiNetworks,
                                         "/IoMgmt/Adapters/wifi0/WifiNetworks" : trees.WifiNetworks,

                                         "wifiProfile" : trees.WifiProfile,
                                         "/IoMgmt/Adapters/wifi0/Profiles/Active" : trees.WifiProfile
                                     })
