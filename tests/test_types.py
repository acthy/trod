"""
tests for types module
"""

from datetime import datetime, date, time, timedelta

import pytest

from trod import db, err, _helper as helper, types as t

from .models import TypesModel as TM


def test_expr():

    age = t.Int(name='age')
    name = t.Char(name='name')
    phone = t.VarChar(name='phone')

    e = (age > 10) & True
    assert helper.parse(e) == helper.Query(
        '((`age` > %s) AND %s);', (10, True)
    )
    e = True & (age > 10)
    assert helper.parse(e) == helper.Query(
        '(%s AND (`age` > %s));', (True, 10,)
    )
    e = False | (age > 10)
    assert helper.parse(e) == helper.Query(
        '(%s OR (`age` > %s));', (False, 10,)
    )
    e = (age > 10) | (name == 'test')
    assert helper.parse(e) == helper.Query(
        '((`age` > %s) OR (`name` = %s));', (10, 'test')
    )
    e = (name == 'test') | (age > 10)
    assert helper.parse(e) == helper.Query(
        '((`name` = %s) OR (`age` > %s));', ('test', 10)
    )
    e = age + 1
    assert helper.parse(e) == helper.Query(
        '(`age` + %s);', (1,)
    )
    e = 1 + age
    assert helper.parse(e) == helper.Query(
        '(%s + `age`);', (1,)
    )
    e = age + '20'
    assert helper.parse(e) == helper.Query(
        '(`age` + %s);', (20,)
    )
    e = 20 + age
    assert helper.parse(e) == helper.Query(
        '(%s + `age`);', (20,)
    )
    e = name + 'name'
    assert helper.parse(e) == helper.Query(
        '(`name` || %s);', ('name',)
    )
    e = 'name' + name
    assert helper.parse(e) == helper.Query(
        '(%s || `name`);', ('name',)
    )
    nickname = t.VarChar(name='nickname')
    e = nickname + name
    assert helper.parse(e) == helper.Query(
        '(`nickname` || `name`);', ()
    )
    e = age - 1
    assert helper.parse(e) == helper.Query(
        '(`age` - %s);', (1,)
    )
    e = 100 - age
    assert helper.parse(e) == helper.Query(
        '(%s - `age`);', (100,)
    )
    e = age * '2'
    assert helper.parse(e) == helper.Query(
        '(`age` * %s);', (2,)
    )
    e = 2 * age
    assert helper.parse(e) == helper.Query(
        '(%s * `age`);', (2,)
    )
    e = 1000 / age
    assert helper.parse(e) == helper.Query(
        '(%s / `age`);', (1000,)
    )
    e = age / 2
    assert helper.parse(e) == helper.Query(
        '(`age` / %s);', (2,)
    )
    e = age ^ name
    assert helper.parse(e) == helper.Query(
        '(`age` # `name`);', ()
    )
    e = 'name' ^ name
    assert helper.parse(e) == helper.Query(
        '(%s # `name`);', ('name',)
    )
    e = name == 'at7h'
    assert helper.parse(e) == helper.Query(
        '(`name` = %s);', ('at7h',)
    )
    e = name != 'at7h'
    assert helper.parse(e) == helper.Query(
        '(`name` != %s);', ('at7h',)
    )
    e = name <= 'at7h'
    assert helper.parse(e) == helper.Query(
        '(`name` <= %s);', ('at7h',)
    )
    e = name >= 'at7h'
    assert helper.parse(e) == helper.Query(
        '(`name` >= %s);', ('at7h',)
    )
    e = age < 90
    assert helper.parse(e) == helper.Query(
        '(`age` < %s);', (90,)
    )
    e = age > 20
    assert helper.parse(e) == helper.Query(
        '(`age` > %s);', (20,)
    )
    e = name >> None
    assert helper.parse(e) == helper.Query(
        '(`name` IS %s);', (None,)
    )
    e = name << ['at7h', 'mejer']
    assert helper.parse(e) == helper.Query(
        '(`name` IN %s);', (('at7h', 'mejer'),)
    )
    e = name % 'at'
    assert helper.parse(e) == helper.Query(
        '(`name` LIKE BINARY %s);', ('at',)
    )
    e = name ** 'at'
    assert helper.parse(e) == helper.Query(
        '(`name` LIKE %s);', ('at',)
    )
    e = age[slice(20, 30)]
    assert helper.parse(e) == helper.Query(
        '(`age` BETWEEN %s AND %s);', (20, 30,)
    )
    e = age[10]
    assert helper.parse(e) == helper.Query(
        '(`age` = %s);', (10,)
    )
    try:
        e = age[slice(20)]
        helper.parse(e)
        assert False
    except ValueError:
        pass

    e = name.concat(10)
    assert helper.parse(e) == helper.Query(
        '(`name` || %s);', ('10',)
    )
    e = name.binand('at7h')
    assert helper.parse(e) == helper.Query(
        '(`name` & %s);', ('at7h',)
    )
    e = name.binor('at7h')
    assert helper.parse(e) == helper.Query(
        '(`name` | %s);', ('at7h',)
    )
    e = name.in_(['at7h', 'mejor'])
    assert helper.parse(e) == helper.Query(
        '(`name` IN %s);', (('at7h', 'mejor'),)
    )
    e = name.in_(helper.SQL("SELECT * FROM `user`"))
    assert helper.parse(e) == helper.Query(
        '(`name` IN (SELECT * FROM `user`));', ()
    )
    e = name.in_(10)
    try:
        helper.parse(e)
        assert False
    except TypeError:
        pass
    e = name.nin_(['at7h', 'mejor'])
    assert helper.parse(e) == helper.Query(
        '(`name` NOT IN %s);', (('at7h', 'mejor'),)
    )
    e = name.exists(['at7h', 'mejor'])
    assert helper.parse(e) == helper.Query(
        '(`name` EXISTS %s);', (('at7h', 'mejor'),)
    )
    e = name.nexists(['at7h', 'mejor'])
    assert helper.parse(e) == helper.Query(
        '(`name` NOT EXISTS %s);', (('at7h', 'mejor'),)
    )
    e = name.isnull()
    assert helper.parse(e) == helper.Query(
        '(`name` IS %s);', (None,)
    )
    e = name.isnull(False)
    assert helper.parse(e) == helper.Query(
        '(`name` IS NOT %s);', (None,)
    )
    e = name.regexp('at.*')
    assert helper.parse(e) == helper.Query(
        '(`name` REGEXP %s);', ('at.*',)
    )
    e = name.regexp('at.*', i=False)
    assert helper.parse(e) == helper.Query(
        '(`name` REGEXP BINARY %s);', ('at.*',)
    )
    e = phone.like(177)
    assert helper.parse(e) == helper.Query(
        '(`phone` LIKE %s);', ('177',)
    )
    e = phone.like(177, i=False)
    assert helper.parse(e) == helper.Query(
        '(`phone` LIKE BINARY %s);', ('177',)
    )
    e = phone.contains(7867)
    assert helper.parse(e) == helper.Query(
        '(`phone` LIKE %s);', ('%7867%',)
    )
    e = phone.contains(7867, i=False)
    assert helper.parse(e) == helper.Query(
        '(`phone` LIKE BINARY %s);', ('%7867%',)
    )
    e = name.endswith('7h')
    assert helper.parse(e) == helper.Query(
        '(`name` LIKE %s);', ('%7h',)
    )
    e = name.endswith('7h', i=False)
    assert helper.parse(e) == helper.Query(
        '(`name` LIKE BINARY %s);', ('%7h',)
    )
    e = name.startswith('at')
    assert helper.parse(e) == helper.Query(
        '(`name` LIKE %s);', ('at%',)
    )
    e = name.startswith('at', i=False)
    assert helper.parse(e) == helper.Query(
        '(`name` LIKE BINARY %s);', ('at%',)
    )
    e = age.between(10, 30)
    assert helper.parse(e) == helper.Query(
        '(`age` BETWEEN %s AND %s);', (10, 30)
    )
    e = age.nbetween(10, 30)
    assert helper.parse(e) == helper.Query(
        '(`age` NOT BETWEEN %s AND %s);', (10, 30)
    )
    e = age.asc()
    assert helper.parse(e) == helper.Query(
        '`age` ASC ;', ()
    )
    e = age.desc()
    assert helper.parse(e) == helper.Query(
        '`age` DESC ;', ()
    )
    e = age.as_('a')
    assert helper.parse(e) == helper.Query(
        '`age` AS `a` ;', ()
    )
    e = age.as_('')
    assert helper.parse(e) == helper.Query(
        '`age`;', ()
    )
    e = (age > 10) & (name == 'test')
    assert helper.parse(e) == helper.Query(
        '((`age` > %s) AND (`name` = %s));', (10, 'test')
    )
    e = (name == 'test') & (age > 10)
    assert helper.parse(e) == helper.Query(
        '((`name` = %s) AND (`age` > %s));', ('test', 10)
    )
    e = (age >= '20') & name.in_(['at7h', 'mejor']) | phone.startswith('153')
    assert helper.parse(e) == helper.Query(
        '(((`age` >= %s) AND (`name` IN %s)) OR (`phone` LIKE %s));',
        (20, ('at7h', 'mejor'), '153%')
    )

    # helper
    sql = helper.SQL("SELECT")
    assert repr(sql) == str(sql) == 'SQL(SELECT)'
    sql = helper.SQL("SELECT * FROM `user` WHERE `id` IN %s", (1, 2, 3))
    assert repr(sql) == str(sql) == 'SQL(SELECT * FROM `user` WHERE `id` IN %s) % (1, 2, 3)'
    assert helper.parse(sql) == helper.Query(
        "SELECT * FROM `user` WHERE `id` IN %s;", (1, 2, 3)
    )
    q = helper.Query("SELECT")
    assert repr(q) == 'Query({})'.format(str(q))
    try:
        q.r = 1
        assert False, 'Should be raise TypeError'
    except TypeError:
        pass
    try:
        assert helper.parse((age > 10) | (name == 'test')) == sql
        assert False, 'Should be raise TypeError'
    except TypeError:
        pass
    assert q.r is True
    q.r = False
    assert q.r is False
    q = helper.Query("SeLeCT FrOm")
    assert q.r is True
    q = helper.Query("SShow")
    assert q.r is True
    q = helper.Query("SSow")
    assert q.r is False
    try:
        assert helper.Query("SELECT", {1: 1}).params
        assert False, 'Should be raise TypeError'
    except TypeError:
        pass
    ctx = helper.Context()
    ctx.literal("SELECT").values("100")
    assert helper.parse(ctx) == helper.Query('SELECT;', ("100",))


def test_fieldbase():
    nickname = t.VarChar()
    try:
        hash(nickname)
        assert False
    except err.NoColumnNameError:
        pass
    assert isinstance(nickname.seqnum, int)
    assert nickname.to_str({}) == '{}'
    try:
        nickname.to_str(None)
        assert False
    except ValueError:
        pass
    nickname = t.VarChar(null=False)
    assert nickname.db_value(1) == '1'


def test_tinyint():
    tinyint = t.Tinyint()
    try:
        assert tinyint.column
        assert tinyint.__def__()
        assert False, "Should be raise NoColumnNameError"
    except err.NoColumnNameError:
        pass
    tinyint = t.Tinyint(name="ty")
    assert tinyint.column == "`ty`"
    assert str(tinyint) == "`ty` tinyint(4) DEFAULT NULL;"

    tinyint = t.Tinyint(name='ty', length=3, null=False, default=1, comment="ty")
    assert str(tinyint) == "`ty` tinyint(3) NOT NULL DEFAULT '1' COMMENT 'ty';"

    tinyint = t.Tinyint(name='ty', unsigned=True, default=1, comment="ty")
    assert str(tinyint) == "`ty` tinyint(4) unsigned DEFAULT '1' COMMENT 'ty';"

    tinyint = t.Tinyint(name='ty', zerofill=True)
    assert str(tinyint) == f"`ty` tinyint(4) zerofill DEFAULT NULL;"

    assert tinyint.py_value('1') == 1
    assert tinyint.db_value('11') == 11

    try:
        assert isinstance(tinyint.db_value('1x'), int)
        assert False, "Should be raise ValueError"
    except ValueError:
        pass


def test_smllint():
    smallint = t.Smallint(name='sl', comment="sl")
    assert smallint.py_value('1') == 1
    assert smallint.db_value('2') == 2
    assert str(smallint) == "`sl` smallint(6) DEFAULT NULL COMMENT 'sl';"
    smallint = t.Smallint(
        name='sl', length=4, unsigned=True, zerofill=True, null=False, default=1, comment="sl"
    )
    assert str(smallint) == "`sl` smallint(4) unsigned zerofill NOT NULL DEFAULT '1' COMMENT 'sl';"


def test_int():
    int_ = t.Int(name='int', comment="int")
    assert str(int_) == "`int` int(11) DEFAULT NULL COMMENT 'int';"
    try:
        int_ = t.Int(name='int', default='xxx')
        assert str(int_)
        assert False, "Should be raise TypeError"
    except TypeError:
        pass
    try:
        int_ = t.Int(name='int', primary_key=True, default=1)
        assert False, "Should be raise ProgrammingError"
    except err.ProgrammingError:
        pass
    try:
        int_ = t.Int(name='int', auto=True)
        assert False, "Should be raise ProgrammingError"
    except err.ProgrammingError:
        pass


def test_bigint():
    bigint = t.Bigint(name='bigint')
    assert str(bigint) == "`bigint` bigint(20) DEFAULT NULL;"
    bigint = t.Bigint(name='bigint', length=18, null=False, default=1)
    assert str(bigint) == "`bigint` bigint(18) NOT NULL DEFAULT '1';"
    try:
        bigint = t.Bigint(name='bigint', primary_key=True, default=1)
        bigint = t.Bigint(name='bigint', auto=True)
        assert False, "Should be raise ProgrammingError"
    except err.ProgrammingError:
        pass
    bigint = t.Bigint(name='bigint', primary_key=True, auto=True)
    assert str(bigint) == "`bigint` bigint(20) NOT NULL AUTO_INCREMENT;"


def test_auto():
    auto = t.Auto(name='auto')
    assert str(auto) == "`auto` int(11) NOT NULL AUTO_INCREMENT;"


def test_bigauto():
    bigauto = t.BigAuto(name='bigauto')
    assert str(bigauto) == "`bigauto` bigint(20) NOT NULL AUTO_INCREMENT;"


def test_bool():
    bool_ = t.Bool(name='bool', null=False, default=True)
    assert str(bool_) == "`bool` bool NOT NULL DEFAULT '1';"
    assert bool_.db_value(0) is False
    assert bool_.py_value(1) is True
    assert bool_.to_str(True) == '1'
    assert bool_.to_str(False) == '0'


def test_float():
    float_ = t.Float(name='float', null=False, default=43.54, length=7)
    assert str(float_) == "`float` float(7) NOT NULL DEFAULT '43.54';"
    float_ = t.Float(name='float', length=(4, 3), default=100.0, unsigned=True)
    assert str(float_) == "`float` float(4,3) unsigned DEFAULT '100.0';"
    try:
        float_ = t.Float(name='float', length=(4, 3, 5))
        float_ = t.Float(name='float', length='7')
        assert False, 'Should be raise TypeError'
    except TypeError:
        pass


def test_double():
    double = t.Double(name='double', null=False, length=7, default=43.54)
    assert str(double) == "`double` double(7) NOT NULL DEFAULT '43.54';"
    double = t.Double(name='double', length=(4, 3), unsigned=True)
    assert str(double) == "`double` double(4,3) unsigned DEFAULT NULL;"
    assert double.py_value(None) is None
    assert double.py_value(0) == 0.0
    try:
        double = t.Double(name='double', length=(4, 3, 5))
        double = t.Double(name='double', length='7')
        assert False, 'Should be raise TypeError'
    except TypeError:
        pass


def test_decimal():
    import decimal as d
    decimal = t.Decimal(name='decimal')
    assert str(decimal) == "`decimal` decimal(10,5) DEFAULT NULL;"
    decimal = t.Decimal(name='decimal', length=(6, 3), default=d.Decimal(str(43.54)))
    assert str(decimal) == "`decimal` decimal(6,3) DEFAULT '43.54';"
    assert decimal.py_value(None) is None
    assert decimal.py_value(0) == d.Decimal(0)
    assert str(decimal.py_value('100.12')) == '100.12'
    assert isinstance(decimal.db_value(10), d.Decimal)
    try:
        decimal = t.Decimal(name='decimal', length=10)
        assert False, 'Should be raise TypeError'
    except TypeError:
        pass
    decimal = t.Decimal(name='decimal', auto_round=True)
    assert decimal.py_value(d.Decimal(10)) == d.Decimal(10)
    assert decimal.db_value(10) == d.Decimal(10)


def test_text():
    text = t.Text(name='text', encoding=t.ENCODING.utf8mb4)
    assert str(text) == "`text` text CHARACTER SET utf8mb4 NULL;"
    assert hasattr(text, 'default') is False
    try:
        text = t.Text(name='text', encoding='utf7')
        assert False
    except ValueError:
        pass
    assert text.py_value(100) == '100'
    assert text.db_value(100) == '100'
    e = text + 'text'
    assert helper.parse(e) == helper.Query('(`text` || %s);', ('text',))
    e = 'text' + text
    assert helper.parse(e) == helper.Query('(%s || `text`);', ('text',))


def test_char():
    char = t.Char(name='char', length=100)
    assert str(char) == "`char` char(100) DEFAULT NULL;"
    try:
        char = t.Char(name='char', encoding='utf7')
        assert False
    except ValueError:
        pass


def test_varchar():
    varchar = t.VarChar(name='varchar', default='c')
    assert str(varchar) == "`varchar` varchar(255) DEFAULT 'c';"
    try:
        varchar = t.VarChar(name='varchar', default=7)
        assert False, 'Should be raise TypeError'
    except TypeError:
        pass


def test_uuid():
    import uuid as uu
    uuid = t.UUID(name='uuid')
    assert str(uuid) == "`uuid` varchar(40) NOT NULL;"
    id_ = str(uu.uuid1())
    assert isinstance(uuid.py_value(id_), uu.UUID)
    assert isinstance(uuid.db_value(uu.uuid1()), str)
    try:
        uuid = t.UUID(primary_key=True, default='uuid')
        assert False
    except err.ProgrammingError:
        pass
    idr = '1a862a72-6a34-4772-8c22-ad8fa3316db5'
    assert uuid.db_value(idr) == '1a862a726a3447728c22ad8fa3316db5'
    assert uuid.db_value('1a862a726a3447728c22ad8fa3316db5') == '1a862a726a3447728c22ad8fa3316db5'
    assert uuid.db_value(uuid) is uuid
    assert uuid.py_value(idr) == uu.UUID(idr)
    assert uuid.py_value(uu.UUID(idr)) == uu.UUID(idr)
    assert uuid.py_value(None) is None


def test_date():
    date_ = t.Date(name='date')
    assert str(date_) == "`date` date DEFAULT NULL;"
    date_ = t.Date(name='date', default=datetime.date)
    assert str(date_) == "`date` date DEFAULT NULL;"
    td = date(2019, 10, 1)
    date_ = t.Date(name='date', default=td)
    assert str(date_) == "`date` date DEFAULT '2019-10-01';"
    assert isinstance(date_.py_value(datetime.now()), date)
    assert isinstance(date_.py_value("2019-10-01"), date)
    assert date_.to_str(td) == "2019-10-01"
    assert isinstance(date_(), date)


def test_time():
    time_ = t.Time(name='time')
    assert str(time_) == "`time` time DEFAULT NULL;"
    time_ = t.Time(name='time', default=datetime.time)
    assert str(time_) == "`time` time DEFAULT NULL;"
    td = time(22, 19, 34)
    time_ = t.Time(name='time', default=td)
    assert str(time_) == "`time` time DEFAULT '22:19:34.000000';"
    assert isinstance(time_.py_value(datetime.now()), time)
    assert isinstance(time_.py_value("10:23:23"), time)
    assert time_.to_str(td) == "22:19:34.000000"

    t.Time.formats = ['%H:%M:%S']
    td = time(22, 19, 34)
    time_ = t.Time(name='time', default=td)
    assert str(time_) == "`time` time DEFAULT '22:19:34';"
    assert time_.to_str(td) == "22:19:34"
    assert isinstance(time_(), time)
    assert isinstance(time_.db_value(timedelta(weeks=7)), time)


def test_datetime():
    datetime_ = t.DateTime(name='dt', formats=['%Y-%m-%d %H:%M:%S'])
    assert str(datetime_) == "`dt` datetime DEFAULT NULL;"
    assert isinstance(datetime_.py_value("2019-10-10 10:23:23"), datetime)
    assert datetime_.to_str(datetime(2019, 10, 10, 10, 23, 23)) == "2019-10-10 10:23:23"
    datetime_ = t.DateTime(name='dt', default=datetime.now)
    assert str(datetime_) == "`dt` datetime DEFAULT NULL;"
    assert datetime_.to_str(datetime(2019, 10, 10, 10, 23, 23)) == "2019-10-10 10:23:23.000000"
    assert isinstance(datetime_(), datetime)


def test_timestamp():
    timestamp = t.Timestamp(name='ts')
    assert str(timestamp) == "`ts` timestamp NULL DEFAULT NULL;"
    assert isinstance(timestamp.py_value("2019-10-10 10:23:23"), datetime)
    assert isinstance(timestamp.to_str(datetime(2019, 10, 10, 10, 23, 23)), str)
    assert isinstance(timestamp.db_value(datetime(2019, 10, 10, 10, 23, 23)), int)
    timestamp = t.Timestamp(name='ts', default=datetime.now)
    assert str(timestamp) == "`ts` timestamp NULL DEFAULT NULL;"
    assert timestamp.db_value(None) is None
    assert isinstance(timestamp.db_value(date(2019, 10, 10)), int)
    assert isinstance(timestamp.db_value(1573984070), int)
    assert isinstance(timestamp.py_value(1573984070), datetime)
    timestamp = t.Timestamp(name='ts', utc=True)
    assert isinstance(timestamp.db_value(1573984070), int)
    assert isinstance(timestamp.py_value(1573984070), datetime)


def test_key():
    age = t.Int(name='age')
    name = t.Char(name='name')
    phone = t.VarChar(name='phone')
    key = t.K('idx_name', name)
    assert str(key) == 'KEY `idx_name` (`name`);'
    key = t.K('idx_name_age', (name, age))
    assert str(key) == 'KEY `idx_name_age` (`name`, `age`);'
    key = t.K('idx_name_age', ('name', 'age'))
    assert str(key) == 'KEY `idx_name_age` (`name`, `age`);'
    key = t.UK('uk_phone', phone, comment='phone')
    assert str(key) == "UNIQUE KEY `uk_phone` (`phone`) COMMENT 'phone';"
    assert repr(key) == "types.UKey(UNIQUE KEY `uk_phone` (`phone`) COMMENT 'phone';)"
    assert key.seqnum == 11
    assert hash(key) == hash('uk_phone')
    try:
        t.K('idx_name', [1, 2, 4])
        assert False
    except TypeError:
        pass


def test_funs():
    age = t.Int(name='age')
    s = t.F.SUM(age).as_('age_sum')
    assert helper.parse(s).sql == 'SUM(`age`) AS `age_sum` ;'

    m_ = t.F.MAX(age).as_('age_max')
    assert helper.parse(m_).sql == 'MAX(`age`) AS `age_max` ;'
    try:
        t.F.STR(age).as_('age_str')
        assert False, 'Should be raise RuntimeError'
    except RuntimeError:
        pass


@pytest.mark.asyncio
async def test_types():

    async with db.Binder():
        await TM.create()
        assert await TM.show().create_syntax() == (
            "CREATE TABLE `test_types_table` (\n"
            "  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'permary_key',\n"
            "  `tinyint` tinyint(1) unsigned zerofill DEFAULT NULL COMMENT 'tinyint',\n"
            "  `smallint` smallint(6) NOT NULL DEFAULT '0' COMMENT 'smallint',\n"
            "  `int_` int(11) unsigned NOT NULL DEFAULT '0' COMMENT 'int',\n"
            "  `bigint` bigint(45) NOT NULL DEFAULT '0' COMMENT 'bigint',\n"
            "  `text` text CHARACTER SET utf8mb4 NOT NULL COMMENT 'text',\n"
            "  `char` char(45) NOT NULL DEFAULT '' COMMENT 'char',\n"
            "  `varchar` varchar(45) NOT NULL DEFAULT '' COMMENT 'varchar',\n"
            "  `uuid` varchar(40) NOT NULL COMMENT 'uuid test',\n"
            "  `float_` float(3,3) DEFAULT '0.000' COMMENT 'float',\n"
            "  `double_` double(4,4) unsigned DEFAULT '0.0000' COMMENT 'double',\n"
            "  `decimal` decimal(10,2) unsigned DEFAULT '0.00' COMMENT 'decimal',\n"
            "  `time_` time DEFAULT NULL COMMENT 'time',\n"
            "  `date_` date DEFAULT NULL COMMENT 'date',\n"
            "  `datetime_` datetime DEFAULT NULL COMMENT 'datetime',\n"
            "  `now_ts` timestamp NULL DEFAULT NULL COMMENT 'now ts',\n"
            "  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created_at',\n"
            "  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON"
            " UPDATE CURRENT_TIMESTAMP COMMENT 'updated_at',\n"
            "  PRIMARY KEY (`id`),\n"
            "  UNIQUE KEY `ukey` (`varchar`) COMMENT 'unique key test',\n"
            "  KEY `key` (`tinyint`,`datetime_`) COMMENT 'key test'\n"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='type case table'"
        )
        await TM.drop()
