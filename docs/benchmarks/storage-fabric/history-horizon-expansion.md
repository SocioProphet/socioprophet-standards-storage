# Storage Fabric History Horizon Expansion

Long-horizon threshold learning should activate only when enough preserved history exists to support learned thresholds.

A storage-fabric history report should expose:
- preserved historical versions
- usable historical versions for the report family
- the minimum learning threshold
- whether long-horizon learning should activate

The existence of preserved history is not enough by itself. Only usable historical versions that contain the relevant benchmark family count toward activation.
