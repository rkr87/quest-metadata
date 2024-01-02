**Features**
- add available_on_rookie flag
- add review summaries
- add app changelogs
- include parsing of google form for mapping unknown package names to store ids
- include parsing of google form for rookie multiplayer reports

**Performance**
- implement multiprocessing/concurrency for image manipulation
- only fetch full version history for new apps and additional ids (fetch released history for all apps)

**Logging/Error Handling**
- Save files for captured errors and keep for x days rather than logging the responses to console
- better timeit implementation
- log more stuff (and accurately)
  
**QoL**
- json schema generation
- enum value generation
- update README.md