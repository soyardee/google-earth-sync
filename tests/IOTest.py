from modules.domtransformer import DOMTransformer

runtime = DOMTransformer(
    "../digest/Sawyer's Places.kmz",
    "../digest/Coworker's Places.kmz",
    "../digest/out.kmz"
)
runtime.process()
runtime.writeOut()
print("{} new locations added".format(runtime.getAppendCount()))
