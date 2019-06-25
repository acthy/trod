import warnings
from collections.abc import Iterable

from trod.utils import TrodDict


OPER = TrodDict(
    AND='AND',
    OR='OR',
    ADD='+',
    SUB='-',
    MUL='*',
    DIV='/',
    BIN_AND='&',
    BIN_OR='|',
    XOR='#',
    MOD='%',
    EQ='=',
    LT='<',
    LTE='<=',
    GT='>',
    GTE='>=',
    NE='!=',
    IN='IN',
    NOT_IN='NOT IN',
    IS='IS',
    IS_NOT='IS NOT',
    LIKE='LIKE',
    ILIKE='ILIKE',
    EXISTS='EXISTS',
    BETWEEN='BETWEEN',
    REGEXP='REGEXP',
    IREGEXP='IREGEXP',
    BITWISE_NEGATION='~'
)


class Cnt:

    def __init__(self, pair, op, encap=False):
        if not encap:
            self.pair = pair
        else:
            self.pair = [f'({p})' for p in pair]
        self.op = op

    @property
    def sql(self):
        return f"{self.pair[0]} {self.op} {self.pair[1]}"


class Expr:

    __slots__ = ('lhs', 'op', 'rhs', 'flat', 'logic')

    def __init__(self, lhs, op, rhs, flat=False, logic=False):
        self.lhs = lhs.name if isinstance(lhs, Column) else lhs
        self.op = op
        self.rhs = rhs.name if isinstance(rhs, Column) else rhs
        self.flat = flat
        self.logic = logic

    def __and__(self, expr):
        if isinstance(expr, self.__class__):
            return self.__class__(self.__sql__(), OPER.AND, expr.__sql__(), logic=True)
        raise ValueError()

    def __or__(self, expr):
        if isinstance(expr, self.__class__):
            return self.__class__(self.__sql__(), OPER.OR, expr.__sql__(), logic=True)
        raise ValueError()

    def __sql__(self):
        if self.op in (OPER.IN, OPER.NOT_IN, OPER.EXISTS):
            if not isinstance(self.rhs, Iterable):
                raise ValueError(
                    f"The value of the operator {self.rhs} should be an Iterable object"
                )
            self.rhs = tuple(self.rhs)
        return Cnt((self.lhs, self.rhs), self.op, encap=self.logic).sql

    def sql(self):
        return self.__sql__()


class Column:

    __slots__ = ('name',)

    def _expr(op, inv=False):  # pylint: disable=all

        def wraper(self, rhs):
            if inv:
                return Expr(rhs, op, self)
            return Expr(self, op, rhs)
        return wraper

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name}>'

    __str__ = __repr__

    __and__ = _expr(OPER.AND)
    __or__ = _expr(OPER.OR)

    __add__ = _expr(OPER.ADD)
    __sub__ = _expr(OPER.SUB)
    __mul__ = _expr(OPER.MUL)
    __div__ = __truediv__ = _expr(OPER.DIV)
    __xor__ = _expr(OPER.XOR)
    __radd__ = _expr(OPER.ADD, inv=True)
    __rsub__ = _expr(OPER.SUB, inv=True)
    __rmul__ = _expr(OPER.MUL, inv=True)
    __rdiv__ = __rtruediv__ = _expr(OPER.DIV, inv=True)
    __rand__ = _expr(OPER.AND, inv=True)
    __ror__ = _expr(OPER.OR, inv=True)
    __rxor__ = _expr(OPER.XOR, inv=True)

    def __eq__(self, rhs):
        op = OPER.IS if rhs is None else OPER.EQ
        return Expr(self, op, rhs)

    def __ne__(self, rhs):
        op = OPER.IS_NOT if rhs is None else OPER.NE
        return Expr(self, op, rhs)

    __lt__ = _expr(OPER.LT)
    __le__ = _expr(OPER.LTE)
    __gt__ = _expr(OPER.GT)
    __ge__ = _expr(OPER.GTE)
    __lshift__ = _expr(OPER.IN)
    __rshift__ = _expr(OPER.IS)
    __mod__ = _expr(OPER.LIKE)
    __pow__ = _expr(OPER.ILIKE)

    b_and = _expr(OPER.BIN_AND)
    b_or = _expr(OPER.BIN_OR)
    in_ = _expr(OPER.IN)
    nin = _expr(OPER.NOT_IN)
    regexp = _expr(OPER.REGEXP)
    iregexp = _expr(OPER.IREGEXP)
    exists = _expr(OPER.EXISTS)
    like = _expr(OPER.LIKE)

    def is_null(self, is_null=True):
        op = OPER.IS if is_null else OPER.IS_NOT
        return Expr(self, op, None)

    def contains(self, rhs):
        return Expr(self, OPER.ILIKE, f'%{rhs}%')

    def startswith(self, rhs):
        return Expr(self, OPER.ILIKE, f'{rhs}%')

    def endswith(self, rhs):
        return Expr(self, OPER.ILIKE, f'%{rhs}')

    def between(self, low, hig):
        return Expr(self, OPER.BETWEEN, Cnt((low, hig), OPER.AND).sql)

    def __getitem__(self, item):
        if isinstance(item, slice):
            if item.start is None or item.stop is None:
                raise ValueError(
                    'BETWEEN range must have both a start and end-point.'
                )
            return self.between(item.start, item.stop)
        return self == item


class FieldBase(Column):

    __slots__ = ('null', 'default', 'comment', '_seq_num')

    _py_type = None
    _db_type = None

    _field_counter = 0
    _spaces = ' '

    # TODO params checker
    def __init__(self, name, null, default, comment):

        if not isinstance(null, bool):
            raise ValueError(f"Unexpected `null` type: {null}")

        super().__init__(name)
        self.null = null
        self.default = default
        self.comment = comment

        FieldBase._field_counter += 1
        self._seq_num = FieldBase._field_counter

    @property
    def _allow_null(self):
        return self.null is True or self.null == 1

    @property
    def _type(self):
        raise NotImplementedError

    @property
    def _stmt(self):

        allow_null = "NULL" if self.allow_null else 'NOT NULL'
        stmt_list = [allow_null]
        if self.default is not None:
            default = self.default
            if isinstance(self, Float):
                default = float(default)
            if not isinstance(default, self._py_type):
                raise ValueError(
                    f'Except default value {self._py_type}, now got {default}'
                )
            if isinstance(default, str):
                default = f"'{self.default}'"
            stmt_list.append(f'DEFAULT {default}')
        elif not self.allow_null:
            warnings.warn(f'Not to give default value for NOT NULL field {self.name}')
        if self.comment:
            stmt_list.append(f"COMMENT '{self.comment}'")
        return self._spaces.join(stmt_list)

    def sql(self):
        return f"{self.type} {self.stmt}"

    @classmethod
    def auto(cls):

        id_field = "`id` bigint(45) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键'"
        return id_field, 'id'

    @property
    def seq_num(self):
        return self._seq_num


class Defi:

    def __init__(self):
        self.sql = []

    def __enter__(self):
        # append _type
        pass

    def __exit__(self):
        # append _comment
        pass

    def _type(self):
        pass

    def _allow_null(self):
        pass

    def _comment(self):
        pass

    def _custom(self):
        pass


class Tinyint(FieldBase):

    __slots__ = ('unsigned', 'length',)

    _py_type = int
    _db_type = 'tinyint'

    _type_tpl = '{type}({length})'

    def __init__(self,
                 length,
                 unsigned=False,
                 null=True,
                 default=None,
                 comment='',
                 name=None):
        super().__init__(
            name=name, null=null, default=default, comment=comment
        )
        self.unsigned = unsigned
        self.length = length

    @property
    def _type(self):
        data_type = self._type_tpl.format(
            type=self._db_type, length=self.length
        )
        if self.unsigned is True:
            data_type = f'{data_type} unsigned'
        return data_type


class Smallint(Tinyint):

    _db_type = 'smallint'


class Int(Tinyint):

    _db_type = 'int'

    def __init__(self,
                 length,
                 unsigned=False,
                 null=True,
                 primary_key=False,
                 default=None,
                 comment='',
                 name=None):
        super().__init__(
            name=name, null=null, default=default,
            comment=comment, length=length, unsigned=unsigned
        )
        self.primary_key = primary_key
        if self.primary_key is True:
            if self.null:
                warnings.warn('Primary_key is not allow null, use default')
            self.null = False
            self.default = None


class Bigint(Int):

    _db_type = 'bigint'


class Text(FieldBase):

    _py_type = str
    _db_type = 'text'
    _type_tpl = '{type}'

    def __init__(self,
                 encoding=None,
                 null=True,
                 comment='',
                 name=None):
        super().__init__(
            name=name, null=null, default=None, comment=comment
        )
        self.encoding = encoding

    @property
    def _type(self):
        return self._type_tpl.format(type=self._db_type)

    @property
    def _stmt(self):
        stmt = []
        if self.encoding is not None:
            stmt.append(f'CHARACTER SET {self.encoding}')
        if self.allow_null:
            stmt.append('NULL')
        else:
            stmt.append('NOT NULL')
        if self.comment:
            stmt.append(f"COMMENT '{self.comment}'")
        return self._spaces.join(stmt)