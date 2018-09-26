"""
Lib for rules
"""

from model import Rule

def get_rules():
    return Rule.query.all()
