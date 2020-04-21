from kmlmodules.domtransformer import DOMTransformer

runtime = DOMTransformer(
    "./digest/test.kmz",
    "./digest/kmz2test.kmz",
)
runtime.process()
runtime.writeOut()
print("{} new locations added".format(runtime.getAppendCount()))
