/home/roddy/GW2_WvWbuilder/backend/tests/test_config.py:6: PytestCollectionWarning: cannot collect test class 'TestSettings' because it has a __init__ constructor (from: tests/test_config.py)
  class TestSettings(BaseSettings):
/home/roddy/GW2_WvWbuilder/backend/tests/archive_duplicates/tests/unit/crud/test_crud_test_base.py:19: PytestCollectionWarning: cannot collect test class 'TestModel' because it has a __init__ constructor (from: tests/archive_duplicates/tests/unit/crud/test_crud_test_base.py)
  class TestModel(Base):
/home/roddy/GW2_WvWbuilder/backend/tests/helpers/test_data.py:486: PytestCollectionWarning: cannot collect test class 'TestDataGenerator' because it has a __init__ constructor (from: tests/helpers/test_data.py)
  class TestDataGenerator:
/home/roddy/GW2_WvWbuilder/backend/tests/unit/test_models_base.py:20: PytestCollectionWarning: cannot collect test class 'TestBase' because it has a __init__ constructor (from: tests/unit/test_models_base.py)
  class TestBase(DeclarativeBase):
/home/roddy/GW2_WvWbuilder/backend/tests/unit/test_models_base.py:25: PytestCollectionWarning: cannot collect test class 'TestSQLModel' because it has a __init__ constructor (from: tests/unit/test_models_base.py)
  class TestSQLModel(TestBase):
/home/roddy/GW2_WvWbuilder/backend/tests/unit/test_models_base.py:38: PytestCollectionWarning: cannot collect test class 'TestSQLUUIDModel' because it has a __init__ constructor (from: tests/unit/test_models_base.py)
  class TestSQLUUIDModel(TestBase):
/home/roddy/GW2_WvWbuilder/backend/tests/unit/test_models_base.py:50: PytestCollectionWarning: cannot collect test class 'TestSQLTimeStampedModel' because it has a __init__ constructor (from: tests/unit/test_models_base.py)
  class TestSQLTimeStampedModel(TestBase):
/home/roddy/GW2_WvWbuilder/backend/tests/unit/test_models_base.py:64: PytestCollectionWarning: cannot collect test class 'TestSQLUUIDTimeStampedModel' because it has a __init__ constructor (from: tests/unit/test_models_base.py)
  class TestSQLUUIDTimeStampedModel(TestBase):
/home/roddy/GW2_WvWbuilder/backend/tests/unit/core/test_core_test_update_async.py:15: PytestCollectionWarning: cannot collect test class 'TestCRUD' because it has a __init__ constructor (from: tests/unit/core/test_core_test_update_async.py)
  class TestCRUD(CRUDBase[ProfessionModel, ProfessionCreate, ProfessionUpdate]):
/home/roddy/GW2_WvWbuilder/backend/tests/unit/crud/test_base.py:18: PytestCollectionWarning: cannot collect test class 'TestCRUDModel' because it has a __init__ constructor (from: tests/unit/crud/test_base.py)
  class TestCRUDModel(Base):
/home/roddy/GW2_WvWbuilder/backend/tests/unit/crud/test_base.py:28: PytestCollectionWarning: cannot collect test class 'TestCRUDCreateSchema' because it has a __init__ constructor (from: tests/unit/crud/test_base.py)
  class TestCRUDCreateSchema(BaseModel):
/home/roddy/GW2_WvWbuilder/backend/tests/unit/crud/test_base.py:35: PytestCollectionWarning: cannot collect test class 'TestCRUDUpdateSchema' because it has a __init__ constructor (from: tests/unit/crud/test_base.py)
  class TestCRUDUpdateSchema(BaseModel):
/home/roddy/.cache/pypoetry/virtualenvs/gw2-wvwbuilder-backend-Ga7h_2Kh-py3.11/lib/python3.11/site-packages/sqlalchemy/orm/decl_api.py:0: PytestCollectionWarning: cannot collect test class 'Base' because it has a __init__ constructor (from: tests/unit/db/test_db_test_base.py)
/home/roddy/GW2_WvWbuilder/backend/tests/unit/db/test_db_test_base.py:13: PytestCollectionWarning: cannot collect test class 'TestModel' because it has a __init__ constructor (from: tests/unit/db/test_db_test_base.py)
  class TestModel(TestBase):
============================= test session starts ==============================
platform linux -- Python 3.11.8, pytest-7.4.4, pluggy-1.6.0
Using --randomly-seed=3983423760
rootdir: /home/roddy/GW2_WvWbuilder/backend
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.11.0, Faker-22.7.0, metadata-3.1.1, asyncio-0.21.2, cov-4.1.0, env-1.1.3, freezegun-0.4.2, factoryboy-2.8.1, mock-3.15.1, html-4.1.1, randomly-3.16.0, xdist-3.8.0, sugar-0.9.7, locust-2.41.5, httpx-0.27.0
asyncio: mode=Mode.AUTO
collected 1123 items / 1 error


---------- coverage: platform linux, python 3.11.8-final-0 -----------
Name                                       Stmts   Miss  Cover   Missing
------------------------------------------------------------------------
app/__init__.py                               23      0   100%
app/api/__init__.py                            0      0   100%
app/api/api_v1/api.py                         16      0   100%
app/api/api_v1/endpoints/__init__.py           5      0   100%
app/api/api_v1/endpoints/auth.py             147    123    16%   37-90, 105-167, 192-231, 241, 247, 263-322, 338-382, 407-425
app/api/api_v1/endpoints/builder.py           19      5    74%   193-248, 265-277, 292
app/api/api_v1/endpoints/builds.py           109     87    20%   127-139, 182-352, 431-448, 478-500, 522-541, 568-585
app/api/api_v1/endpoints/compositions.py     103     85    17%   17-69, 91-125, 134-148, 164-179, 194-211, 223-235, 249-272, 284-303
app/api/api_v1/endpoints/dashboard.py         42     32    24%   47-76, 94-175
app/api/api_v1/endpoints/gw2.py               58     42    28%   29-38, 51-60, 78-92, 106-115, 124-128, 144-153
app/api/api_v1/endpoints/health.py            10      6    40%   22-29
app/api/api_v1/endpoints/metrics.py           22     12    45%   33-41, 57-63, 79-93
app/api/api_v1/endpoints/professions.py       86     62    28%   23-24, 37-44, 55-60, 74-82, 95-101, 122-131, 160-184, 197-200, 219-251, 269-282
app/api/api_v1/endpoints/roles.py             35     21    40%   22-23, 36-43, 57-63, 74-80, 93-99
app/api/api_v1/endpoints/tags.py              68     51    25%   34-51, 73-76, 89-99, 113-126, 140-168, 181-203
app/api/api_v1/endpoints/team_members.py      76     67    12%   39-101, 117-171, 186-239
app/api/api_v1/endpoints/teams.py             72     53    26%   36-47, 60-71, 83-104, 118-143, 156-176, 191-203, 216-239
app/api/api_v1/endpoints/users.py             63     43    32%   25-26, 39-46, 59-60, 72, 85-103, 117-124, 139-154, 169-184
app/api/dependencies.py                       39     39     0%   8-192
app/api/deps.py                               91     74    19%   57-128, 146-148, 166-168, 184, 207-245, 254, 280-297, 323-331
app/api/exception_handlers.py                 17     10    41%   12, 21-24, 33-39, 48, 57, 64
app/api/middleware.py                         14     14     0%   12-249
app/config.py                                  3      3     0%   34-36
app/core/__init__.py                           8      0   100%
app/core/cache.py                             29     18    38%   29-58
app/core/caching.py                           26     26     0%   5-188
app/core/config.py                            19     14    26%   186-229, 240
app/core/database.py                          70     41    41%   86, 119, 153-154, 157-174, 186-205, 211, 216, 223-225, 240-248
app/core/database_utils.py                    65     54    17%   35-58, 62-95, 106-129, 137-167, 177-178
app/core/db_monitor.py                        91     67    26%   41, 83-88, 92-100, 116-222, 238-264, 280-338, 342-378
app/core/deps.py                              21     21     0%   5-66
app/core/exceptions.py                         1      0   100%
app/core/gw2/__init__.py                       4      0   100%
app/core/gw2/cache.py                         58     47    19%   43-48, 53-68, 72-83, 87-98, 109-125
app/core/gw2/client.py                       148    112    24%   66-68, 72-73, 78-80, 85-88, 92-99, 116-160, 164-168, 172-178, 182-207, 214-216, 220-222, 226-229, 234, 238-242, 246, 253, 257, 263-267, 271-275, 280-285, 289-292, 298-304, 314
app/core/gw2/exceptions.py                     0      0   100%
app/core/gw2/models.py                         2      0   100%
app/core/hashing.py                           39     35    10%   32-48, 66-85, 103-110
app/core/key_rotation.py                      37     22    41%   57-58, 62, 66, 70-71, 79-95, 110-131, 140
app/core/key_rotation_service.py              48     48     0%   9-209
app/core/limiter.py                           54     45    17%   28-50, 55-75, 80-85, 108, 113-132
app/core/logging.py                           19     19     0%   10-174
app/core/logging_config.py                    14      0   100%
app/core/middleware.py                        11     11     0%   8-218
app/core/optimizer/__init__.py                 2      0   100%
app/core/optimizer/engine.py                 194    167    14%   53, 80, 84, 88, 92, 96, 116, 139, 148-363, 374-422, 432-504, 517-569, 581-678, 696-727, 744-745
app/core/optimizer/mode_effects.py            48     32    33%   135-143, 156-164, 176-191, 200-213, 231-257, 274-281
app/core/pagination.py                         7      7     0%   5-77
app/core/performance.py                       18     18     0%   10-91
app/core/security.py                          84     84     0%   1-286
app/core/security/__init__.py                  3      0   100%
app/core/security/jwt.py                     159    130    18%   15-17, 36-38, 238-304, 322-354, 376-399, 418-421, 446-460, 478-482, 500-505, 518-526, 543-549, 566-595, 609-623
app/core/security/keys.py                     92     58    37%   55, 57, 62-65, 69-91, 95, 99-100, 104-117, 122-123, 127-128, 134, 147-164, 168-181, 190-193, 205-206, 215, 228
app/core/security/password_utils.py           52     45    13%   29-41, 57-70, 87-92, 105-107, 120-127, 140-160
app/core/tasks/__init__.py                     2      2     0%   9-12
app/core/tasks/key_rotation_task.py           22     22     0%   15-156
app/core/utils.py                             37     37     0%   7-144
app/core/webhook_helpers.py                    5      3    40%   18-24
app/crud/__init__.py                          15      0   100%
app/crud/base.py                               7      0   100%
app/crud/base_async.py                         5      0   100%
app/crud/build.py                              9      0   100%
app/crud/crud_build.py                         4      0   100%
app/crud/crud_composition.py                   4      0   100%
app/crud/crud_elite_specialization.py          5      0   100%
app/crud/crud_permission.py                    4      0   100%
app/crud/crud_profession.py                    5      0   100%
app/crud/crud_role.py                          4      0   100%
app/crud/crud_tag.py                           5      0   100%
app/crud/crud_team.py                          4      0   100%
app/crud/crud_team_member.py                   4      0   100%
app/crud/crud_webhook.py                       2      0   100%
app/crud/elite_specialization.py               6      6     0%   3-125
app/crud/profession.py                         4      0   100%
app/crud/role.py                               8      1    88%   16
app/crud/user.py                               5      0   100%
app/db/__init__.py                            12      0   100%
app/db/base.py                                 1      0   100%
app/db/base_class.py                          21     21     0%   7-71
app/db/db_config.py                           10      4    60%   20-21, 84-85
app/db/dependencies.py                        11      8    27%   21-29
app/db/factories.py                            3      0   100%
app/db/session.py                             29     19    34%   33-38, 48-54, 75-79, 90-98
app/lifespan.py                               28     28     0%   11-77
app/main.py                                  118     72    39%   30-102, 142-151, 166-167, 176-181, 195, 204, 214-229, 239-254, 262, 267
app/models/__init__.py                        20      0   100%
app/models/association_tables.py               5      0   100%
app/models/base.py                             6      0   100%
app/models/base_model.py                      10      0   100%
app/models/build.py                            6      0   100%
app/models/composition.py                     12      4    67%   16-19
app/models/composition_tag.py                  5      1    80%   17
app/models/elite_specialization.py             6      1    83%   19
app/models/enums.py                            1      0   100%
app/models/permission.py                       7      1    86%   17
app/models/profession.py                       8      2    75%   21-22
app/models/registry.py                        16     16     0%   9-46
app/models/role.py                             9      2    78%   18-19
app/models/tag.py                              6      1    83%   16
app/models/team.py                            10      4    60%   17-20
app/models/team_member.py                      7      2    71%   17-18
app/models/token.py                            2      0   100%
app/models/token_models.py                     6      0   100%
app/models/user.py                            13      6    54%   19-24
app/models/user_role.py                       15      3    80%   14-15, 47
app/models/webhook.py                          4      0   100%
app/schemas/__init__.py                       13      0   100%
app/schemas/build.py                           2      0   100%
app/schemas/composition.py                     2      0   100%
app/schemas/elite_specialization.py            2      0   100%
app/schemas/msg.py                             0      0   100%
app/schemas/permission.py                      1      0   100%
app/schemas/profession.py                      3      0   100%
app/schemas/response.py                       20     14    30%   123-133, 150-160, 178-180
app/schemas/role.py                            1      0   100%
app/schemas/tag.py                             1      0   100%
app/schemas/team.py                            3      0   100%
app/schemas/team_member.py                     1      0   100%
app/schemas/token.py                           1      0   100%
app/schemas/user.py                            3      0   100%
app/schemas/webhook.py                         2      0   100%
app/services/gw2_api.py                      120    105    12%   124-203, 212, 218-219, 225-239, 243-244, 250-263, 267-268, 276-293, 297-298, 309-360
app/services/webhook_service.py              189    157    17%   71-102, 119-133, 153-174, 178-185, 189-196, 200-204, 210-233, 237-250, 255-263, 283-312, 318-340, 346-353, 357-369, 379-414, 430
app/worker.py                                 46     46     0%   3-136
------------------------------------------------------------------------
TOTAL                                       3524   2538    28%
Coverage HTML written to dir htmlcov
Coverage XML written to file coverage.xml

Required test coverage of 20% reached. Total coverage: 27.98%
=========================== short test summary info ============================
ERROR tests/integration/optimizer/test_builder_endpoints.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
============================== 1 error in 12.82s ===============================
