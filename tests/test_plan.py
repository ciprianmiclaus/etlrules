from etlrules.plan import Plan
from etlrules.backends.pandas import ProjectRule, RenameRule, SortRule


def test_plan_rules():
    plan = Plan(name="Test Plan", description="This is a plan to test the plan.", strict=True)
    rules_in = [
        SortRule(['A']),
        ProjectRule(['A', 'B']),
        RenameRule({'A': 'AA', 'B': 'BB'}),
    ]
    for rule in rules_in:
        plan.add_rule(rule)
    for idx, rule in enumerate(plan):
        assert rule == rules_in[idx]


def test_plan_to_from_dict():
    plan = Plan(name="Test Plan", description="This is a plan to test the plan.", strict=True)
    plan.add_rule(SortRule(['A']))
    plan.add_rule(ProjectRule(['A', 'B']))
    plan.add_rule(RenameRule({'A': 'AA', 'B': 'BB'}))
    dct = plan.to_dict()
    assert dct["name"] == "Test Plan"
    assert dct["description"] == "This is a plan to test the plan."
    assert dct["strict"] == True
    assert len(dct["rules"]) == 3
    plan2 = Plan.from_dict(dct, "pandas")
    assert plan == plan2


def test_plan_to_from_yaml():
    plan = Plan(name="Test Plan", description="This is a plan to test the plan.", strict=True)
    plan.add_rule(SortRule(['A']))
    plan.add_rule(ProjectRule(['A', 'B']))
    plan.add_rule(RenameRule({'A': 'AA', 'B': 'BB'}))
    yml = plan.to_yaml()
    plan2 = Plan.from_yaml(yml, "pandas")
    assert plan == plan2
