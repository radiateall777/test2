"""SICP 风格的约束传播系统：摄氏度 ↔ 华氏度双向转换。

关系：9 * C = 5 * (F - 32)
"""


def has_value(connector):
    return connector["has_value"]()


def get_value(connector):
    return connector["value"]()


def set_value(connector, new_value, informant):
    connector["set_value"](new_value, informant)


def forget_value(connector, retractor):
    connector["forget"](retractor)


def connect(connector, new_constraint):
    connector["connect"](new_constraint)


def inform_about_value(constraint):
    constraint["process_new_value"]()


def inform_about_no_value(constraint):
    constraint["process_forget_value"]()


def for_each_except(exception, procedure, items):
    for item in items:
        if item is not exception:
            procedure(item)


def connector(name=None):
    """保存一个值，并通知所有连接的约束。"""
    value = [None]
    informant = [None]
    constraints = []

    def has_value_p():
        return informant[0] is not None

    def value_p():
        return value[0]

    def set_value_p(new_value, setter):
        if not has_value_p():
            value[0] = new_value
            informant[0] = setter
            for_each_except(setter, inform_about_value, constraints)
        elif value[0] != new_value:
            raise ValueError(f"Contradiction: {value[0]} vs {new_value}")

    def forget_value_p(retractor):
        if retractor is informant[0]:
            informant[0] = None
            for_each_except(retractor, inform_about_no_value, constraints)

    def connect_p(new_constraint):
        if new_constraint not in constraints:
            constraints.append(new_constraint)
        if has_value_p():
            inform_about_value(new_constraint)

    def me(request):
        if request == "has_value":
            return has_value_p
        if request == "value":
            return value_p
        if request == "set_value":
            return set_value_p
        if request == "forget":
            return forget_value_p
        if request == "connect":
            return connect_p
        raise ValueError(f"Unknown operation: {request}")

    return {
        "has_value": has_value_p,
        "value": value_p,
        "set_value": set_value_p,
        "forget": forget_value_p,
        "connect": connect_p,
        "name": name,
        "__call__": me,
    }


def adder(a1, a2, sum_):
    """约束：a1 + a2 = sum_"""

    def process_new_value():
        if has_value(a1) and has_value(a2):
            set_value(sum_, get_value(a1) + get_value(a2), me)
        elif has_value(a1) and has_value(sum_):
            set_value(a2, get_value(sum_) - get_value(a1), me)
        elif has_value(a2) and has_value(sum_):
            set_value(a1, get_value(sum_) - get_value(a2), me)

    def process_forget_value():
        forget_value(sum_, me)
        forget_value(a1, me)
        forget_value(a2, me)
        process_new_value()

    me = {
        "process_new_value": process_new_value,
        "process_forget_value": process_forget_value,
    }
    connect(a1, me)
    connect(a2, me)
    connect(sum_, me)
    return me


def multiplier(m1, m2, product):
    """约束：m1 * m2 = product"""

    def process_new_value():
        if (has_value(m1) and get_value(m1) == 0) or (
            has_value(m2) and get_value(m2) == 0
        ):
            set_value(product, 0, me)
        elif has_value(m1) and has_value(m2):
            set_value(product, get_value(m1) * get_value(m2), me)
        elif has_value(product) and has_value(m1):
            set_value(m2, get_value(product) / get_value(m1), me)
        elif has_value(product) and has_value(m2):
            set_value(m1, get_value(product) / get_value(m2), me)

    def process_forget_value():
        forget_value(product, me)
        forget_value(m1, me)
        forget_value(m2, me)
        process_new_value()

    me = {
        "process_new_value": process_new_value,
        "process_forget_value": process_forget_value,
    }
    connect(m1, me)
    connect(m2, me)
    connect(product, me)
    return me


def constant(connector_obj, value):
    """将 connector 固定为常量。"""
    me = {
        "process_new_value": lambda: None,
        "process_forget_value": lambda: None,
    }
    connect(connector_obj, me)
    set_value(connector_obj, value, me)
    return me


def converter(c, f):
    """用约束条件连接 c 到 f，将摄氏度转换为华氏度。"""
    u, v, w, x, y = [connector() for _ in range(5)]
    multiplier(c, w, u)
    multiplier(v, x, u)
    adder(v, y, f)
    constant(w, 9)
    constant(x, 5)
    constant(y, 32)


def probe(name, connector_obj):
    """在 connector 值变化时打印。"""

    def print_probe(value):
        print(f"Probe: {name} = {value}")

    def process_new_value():
        print_probe(get_value(connector_obj))

    def process_forget_value():
        print_probe("?")

    me = {
        "process_new_value": process_new_value,
        "process_forget_value": process_forget_value,
    }
    connect(connector_obj, me)
    return me


if __name__ == "__main__":
    C = connector("Celsius")
    F = connector("Fahrenheit")
    converter(C, F)
    probe("Celsius temp", C)
    probe("Fahrenheit temp", F)

    # C → F：100°C = 212°F
    set_value(C, 100, "user")
    # Probe: Celsius temp = 100
    # Probe: Fahrenheit temp = 212.0

    forget_value(C, "user")
    # Probe: Celsius temp = ?
    # Probe: Fahrenheit temp = ?

    # F → C：32°F = 0°C
    set_value(F, 32, "user")
    # Probe: Fahrenheit temp = 32
    # Probe: Celsius temp = 0.0
