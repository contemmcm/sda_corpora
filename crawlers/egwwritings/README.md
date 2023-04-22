# EGW Writings Corpus

```bash
NUM_THREADS=`nproc`
time python3 -u -m crawlers.egwwritings.enumerate
time python3 -u -m crawlers.egwwritings.crawler --n_threads $NUM_THREADS
```
