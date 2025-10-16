# [1.6.0](https://github.com/danielkaldheim/ha_airstage/compare/v1.5.1...v1.6.0) (2025-10-16)


### Features

* **hmn detection:** Adding Human Sensor ([b2c5a8e](https://github.com/danielkaldheim/ha_airstage/commit/b2c5a8e77ed720154f76d1e97a74997e20b62540))

## [1.5.1](https://github.com/danielkaldheim/ha_airstage/compare/v1.5.0...v1.5.1) (2025-09-08)


### Bug Fixes

* **error handling:** fixing broken error result handling in config flow ([d8d9d1e](https://github.com/danielkaldheim/ha_airstage/commit/d8d9d1e4f89ab071dfb86ceb7fe0db10f5753c98))

# [1.5.0](https://github.com/danielkaldheim/ha_airstage/compare/v1.4.8...v1.5.0) (2025-08-11)


### Features

* **fan speed:** support reading (no writing) medium-low and medium-high fan speeds ([942f0aa](https://github.com/danielkaldheim/ha_airstage/commit/942f0aa5e37015c940e271df12b8ef56aa5c55e0))

## [1.4.8](https://github.com/danielkaldheim/ha_airstage/compare/v1.4.7...v1.4.8) (2025-08-08)


### Bug Fixes

* **error handling:** hardening for transient availability cases, maybe ([6045243](https://github.com/danielkaldheim/ha_airstage/commit/60452438ee14af9ea40c1f6b28b1e3068f50765d))

## [1.4.7](https://github.com/danielkaldheim/ha_airstage/compare/v1.4.6...v1.4.7) (2025-08-07)


### Bug Fixes

* **reconfigure:** [#85](https://github.com/danielkaldheim/ha_airstage/issues/85) Reworking workflows for ip address change ([422d967](https://github.com/danielkaldheim/ha_airstage/commit/422d967b3544982c66962a2fadf875e0562d6209))

## [1.4.6](https://github.com/danielkaldheim/ha_airstage/compare/v1.4.5...v1.4.6) (2025-08-06)


### Bug Fixes

* **debug:** removing pyairstage from logging configuration in attempt to improve debug logging usability ([821d3cb](https://github.com/danielkaldheim/ha_airstage/commit/821d3cb3e3b7072275992d0e4ce7ad68e2d444ef))

## [1.4.5](https://github.com/danielkaldheim/ha_airstage/compare/v1.4.4...v1.4.5) (2025-08-06)


### Bug Fixes

* **setup:** [#90](https://github.com/danielkaldheim/ha_airstage/issues/90) improving logging for failures adding new device ([c4689d0](https://github.com/danielkaldheim/ha_airstage/commit/c4689d08ea84cab8070161a60b1491b502effa5f))

## [1.4.4](https://github.com/danielkaldheim/ha_airstage/compare/v1.4.3...v1.4.4) (2025-06-07)


### Bug Fixes

* **climate:** [#70](https://github.com/danielkaldheim/ha_airstage/issues/70) hacking in a fallback for min/max temperatures when off / fan mode ([20877d2](https://github.com/danielkaldheim/ha_airstage/commit/20877d27e797bc3f382540d34be21935445848d4))

## [1.4.3](https://github.com/danielkaldheim/ha_airstage/compare/v1.4.2...v1.4.3) (2025-06-06)


### Bug Fixes

* **configuration:** [#75](https://github.com/danielkaldheim/ha_airstage/issues/75) Fixing config flow ([c9c384c](https://github.com/danielkaldheim/ha_airstage/commit/c9c384cfeca6601aa00b43cfe41eb03fb11e0bed))

## [1.4.2](https://github.com/danielkaldheim/ha_airstage/compare/v1.4.1...v1.4.2) (2025-05-14)


### Bug Fixes

* **requirements:** establishing minimum HA version ([1376669](https://github.com/danielkaldheim/ha_airstage/commit/13766696b84187cc4ec400aba3b2252b138fa2d6))

## [1.4.1](https://github.com/danielkaldheim/ha_airstage/compare/v1.4.0...v1.4.1) (2025-05-12)


### Bug Fixes

* **manifest:** correcting automation of manifest.json ([16a7fe2](https://github.com/danielkaldheim/ha_airstage/commit/16a7fe2350fe0094a4111fcd1fcf5da49967b9b1))

# [1.4.0](https://github.com/danielkaldheim/ha_airstage/compare/v1.3.3...v1.4.0) (2025-05-12)


### Features

* **temperature:** Integrating HA min/max temperature properties ([73e2f72](https://github.com/danielkaldheim/ha_airstage/commit/73e2f729a1f59766f218f3352cec52b205c3a4ce))

## [1.3.3](https://github.com/danielkaldheim/ha_airstage/compare/v1.3.2...v1.3.3) (2025-05-02)


### Bug Fixes

* **set_temperature:** [#12](https://github.com/danielkaldheim/ha_airstage/issues/12) support hvac_mode with set_temperature ([540294a](https://github.com/danielkaldheim/ha_airstage/commit/540294abbe40fb133e079e560b2d1ab812ef3d74))

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
