def breadth_signal(cap_return, equal_return):
    if cap_return > 0 and equal_return > 0:
        return "healthy"
    elif cap_return > 0 > equal_return:
        return "fragile"
    else:
        return "risk_off"
