## [1.3.2](https://github.com/danielkaldheim/ha_airstage/compare/v1.3.1...v1.3.2) (2025-04-25)


### Bug Fixes

* **ci:** bump version ([3cb56cb](https://github.com/danielkaldheim/ha_airstage/commit/3cb56cbfd056ca038f2db063ff4d3ac3788ecde0))

## [1.3.1](https://github.com/danielkaldheim/ha_airstage/compare/v1.3.0...v1.3.1) (2025-04-13)


### Bug Fixes

* **dhcp:** Using updated DhcpServiceInfo before 2026 deadline ([9bb641c](https://github.com/danielkaldheim/ha_airstage/commit/9bb641c645231ffcbfe7e5c5b19622f514258d67))

# [1.3.0](https://github.com/danielkaldheim/ha_airstage/compare/v1.2.4...v1.3.0) (2025-04-13)


### Features

* **swing:** Leveraging reworking pyairstage to allow swing positions for 4 or 6 position devices ([f750273](https://github.com/danielkaldheim/ha_airstage/commit/f7502734ef20765124ad4a827b5d3f2b67409403))

## [1.2.4](https://github.com/danielkaldheim/ha_airstage/compare/v1.2.3...v1.2.4) (2025-01-13)


### Reverts

* Revert "Trying a different plugin for updating manifest.json" ([c691128](https://github.com/danielkaldheim/ha_airstage/commit/c691128392970f21e5d64a06e4bfe03693a3ac45))

## [1.2.3](https://github.com/danielkaldheim/ha_airstage/compare/v1.2.2...v1.2.3) (2025-01-12)


### Bug Fixes

* **climate:** max temp is 30, not 32 ([b0684df](https://github.com/danielkaldheim/ha_airstage/commit/b0684df8c24d3c69b47f43f8f30f27617e8f3138))

## [1.2.2](https://github.com/danielkaldheim/ha_airstage/compare/v1.2.1...v1.2.2) (2024-12-25)


### Bug Fixes

* **ci:** disable ha-blueprint because requested access to the resource is denied ([1729340](https://github.com/danielkaldheim/ha_airstage/commit/1729340a6384d14f11183dfad4253a4817716ba1))

## [1.2.1](https://github.com/danielkaldheim/ha_airstage/compare/v1.2.0...v1.2.1) (2024-11-18)


### Bug Fixes

* **docs:** bringing back strings.json in proper format ([5d3f8c7](https://github.com/danielkaldheim/ha_airstage/commit/5d3f8c72ad1ba63ed15bcfecb3e24b96c4b3bdc5))

# [1.2.0](https://github.com/danielkaldheim/ha_airstage/compare/v1.1.9...v1.2.0) (2024-11-18)


### Features

* **config:** added ability to turn on unit when setting temp while unit is off ([#36](https://github.com/danielkaldheim/ha_airstage/issues/36)). Thanks uvera! ([3fb9184](https://github.com/danielkaldheim/ha_airstage/commit/3fb91846805390a26e39d08108f9f26f98f842fe))

## [1.1.9](https://github.com/danielkaldheim/ha_airstage/compare/v1.1.8...v1.1.9) (2024-08-24)


### Bug Fixes

* **climate:** fixes climate entity min heat and on/off ([1a34777](https://github.com/danielkaldheim/ha_airstage/commit/1a34777066d2e741ae5be8a9ff33b7a309b5cfba))

## [1.1.8](https://github.com/danielkaldheim/ha_airstage/compare/v1.1.7...v1.1.8) (2024-03-20)


### Bug Fixes

* **api:** bump api version ([46aa13d](https://github.com/danielkaldheim/ha_airstage/commit/46aa13de328f88d51c00814cae4e56a020ad06c1))

## [1.1.7](https://github.com/danielkaldheim/ha_airstage/compare/v1.1.6...v1.1.7) (2023-11-02)


### Bug Fixes

* **climate:** Quickfix target temperature is none, issue [#16](https://github.com/danielkaldheim/ha_airstage/issues/16) ([fc2e313](https://github.com/danielkaldheim/ha_airstage/commit/fc2e31340a8edaa1ace6aa34f14886cb142b095e))

## [1.1.6](https://github.com/danielkaldheim/ha_airstage/compare/v1.1.5...v1.1.6) (2023-10-17)


### Bug Fixes

* **target temperature:** fix set target temperature when mode is fan only ([482b6e3](https://github.com/danielkaldheim/ha_airstage/commit/482b6e39ff84ff3bdccdb6a8f01a38252210ee9f))

## [1.1.5](https://github.com/danielkaldheim/ha_airstage/compare/v1.1.4...v1.1.5) (2023-10-17)


### Bug Fixes

* **feature:** add back target temperature feature ([56f6642](https://github.com/danielkaldheim/ha_airstage/commit/56f66421935adde6b5add5e3d88d9b6876d6cfb9))

## [1.1.4](https://github.com/danielkaldheim/ha_airstage/compare/v1.1.3...v1.1.4) (2023-10-17)


### Bug Fixes

* **target temperature:** get last good value if value returns error ([5b8e858](https://github.com/danielkaldheim/ha_airstage/commit/5b8e858fdcd2a03b3233ad53b4dfc37130275010))

## [1.1.3](https://github.com/danielkaldheim/ha_airstage/compare/v1.1.2...v1.1.3) (2023-10-11)


### Bug Fixes

* **target temperature:** disable setting temperature when feature is off ([b4c19fd](https://github.com/danielkaldheim/ha_airstage/commit/b4c19fdf9e85d48347d470c7e49e15aeab50e823))

## [1.1.2](https://github.com/danielkaldheim/ha_airstage/compare/v1.1.1...v1.1.2) (2023-10-07)


### Bug Fixes

* **docs:** update docs regarding cloud ([9812f26](https://github.com/danielkaldheim/ha_airstage/commit/9812f26d0699774a5b3ee10ec5448be2ab2d2bd2))

## [1.1.1](https://github.com/danielkaldheim/ha_airstage/compare/v1.1.0...v1.1.1) (2023-10-07)


### Bug Fixes

* **config flow:** remove cloud, fixes [#7](https://github.com/danielkaldheim/ha_airstage/issues/7) ([339f3e3](https://github.com/danielkaldheim/ha_airstage/commit/339f3e31cf7af09b126e7f8b7ea75d68cc4a8d50))
* **fan mode:** fix target temperature issue [#4](https://github.com/danielkaldheim/ha_airstage/issues/4) ([0a3da77](https://github.com/danielkaldheim/ha_airstage/commit/0a3da779ee324a395411157117aca85132a8f633))
* **Occupancy:** Removed Occupancy sensory, wrong info ([45ffc35](https://github.com/danielkaldheim/ha_airstage/commit/45ffc35520afb935a2a2c500c9219a48c9fd7b97))

# [1.1.0](https://github.com/danielkaldheim/ha_airstage/compare/v1.0.7...v1.1.0) (2023-08-18)


### Bug Fixes

* **version:** bump pyairstage version ([9668ef4](https://github.com/danielkaldheim/ha_airstage/commit/9668ef44c81a3b8a9f33896d8efccc0a926c4d81))


### Features

* **human detection:** added occupancy binary sensor for units with this functionality ([d18fc4b](https://github.com/danielkaldheim/ha_airstage/commit/d18fc4b4ec6c18a8e176da1a75a69de2ce4ecb7f))

## [1.0.7](https://github.com/danielkaldheim/ha_airstage/compare/v1.0.6...v1.0.7) (2023-08-16)


### Bug Fixes

* **config:** added better validation and error handling on local ([0f92e5a](https://github.com/danielkaldheim/ha_airstage/commit/0f92e5ac964febc9c03afa678d8b4d84e7ec1e27))
* **led:** added missing led option ([5f36c3a](https://github.com/danielkaldheim/ha_airstage/commit/5f36c3a6b1a48ab792509c94739b931151aba679))
* **requirements:** bump pyairstage to 1.0.4 ([92cadc5](https://github.com/danielkaldheim/ha_airstage/commit/92cadc5a7ef6392f12d36366b3278a2946454cd6))

## [1.0.6](https://github.com/danielkaldheim/ha_airstage/compare/v1.0.5...v1.0.6) (2023-08-15)


### Bug Fixes

* **import:** hotfix, typo in import ([e952a5f](https://github.com/danielkaldheim/ha_airstage/commit/e952a5f76171f8d60cddc8b7ed1de5fed03b6052))

## [1.0.5](https://github.com/danielkaldheim/ha_airstage/compare/v1.0.4...v1.0.5) (2023-08-15)


### Bug Fixes

* **supported features:** validate feature ([dcfed13](https://github.com/danielkaldheim/ha_airstage/commit/dcfed13a54ad9678e9505d2584ea63e4eb254d12))

## [1.0.4](https://github.com/danielkaldheim/ha_airstage/compare/v1.0.3...v1.0.4) (2023-08-14)


### Bug Fixes

* **name:** update name ([52118c9](https://github.com/danielkaldheim/ha_airstage/commit/52118c94512cb33f0a3e2dc916b46baef5937495))
