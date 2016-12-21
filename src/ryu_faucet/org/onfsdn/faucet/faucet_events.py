from ryu.controller import event

class EventFaucetReconfigure(event.EventBase):
    """Event used to trigger FAUCET reconfiguration."""
    pass

class EventFaucetResolveGateways(event.EventBase):
    """Event used to trigger gateway re/resolution."""
    pass


class EventFaucetHostExpire(event.EventBase):
    """Event used to trigger expiration of host state in controller."""
    pass
