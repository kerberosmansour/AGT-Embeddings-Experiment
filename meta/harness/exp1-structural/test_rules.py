#!/usr/bin/env python3
"""Truth-table BDD tests for Experiment 1 structural rules."""

import unittest

import rules as RU


class TestRuleTruth(unittest.TestCase):
    def m(self, **kw):
        base = {"requires_tool_call": False, "contains_sensitive_sink": False,
                "source_type": "document", "trust_level": "untrusted"}
        base.update(kw)
        return base

    def test_R1(self):
        self.assertTrue(RU.R1(self.m(trust_level="untrusted", requires_tool_call=True)))
        self.assertFalse(RU.R1(self.m(trust_level="authenticated_user", requires_tool_call=True)))
        self.assertFalse(RU.R1(self.m(trust_level="untrusted", requires_tool_call=False)))

    def test_R2(self):
        self.assertTrue(RU.R2(self.m(contains_sensitive_sink=True, source_type="document", trust_level="untrusted")))
        self.assertFalse(RU.R2(self.m(contains_sensitive_sink=True, source_type="user", trust_level="authenticated_user")))
        self.assertFalse(RU.R2(self.m(contains_sensitive_sink=False)))

    def test_R3_strict(self):
        self.assertTrue(RU.R3(self.m(trust_level="untrusted", requires_tool_call=True, contains_sensitive_sink=True)))
        self.assertFalse(RU.R3(self.m(trust_level="untrusted", requires_tool_call=True, contains_sensitive_sink=False)))

    def test_R4_union(self):
        for tl in RU.TRUST_VALUES:
            for st in RU.SOURCE_TYPE_VALUES:
                for tool in (True, False):
                    for sink in (True, False):
                        mm = self.m(trust_level=tl, source_type=st, requires_tool_call=tool, contains_sensitive_sink=sink)
                        self.assertEqual(RU.R4(mm), RU.R1(mm) or RU.R2(mm))

    def test_R3_subset_of_R1(self):
        for tl in RU.TRUST_VALUES:
            for tool in (True, False):
                for sink in (True, False):
                    mm = self.m(trust_level=tl, requires_tool_call=tool, contains_sensitive_sink=sink)
                    if RU.R3(mm):
                        self.assertTrue(RU.R1(mm))

    def test_coarse_source(self):
        self.assertEqual(RU.coarse_source({"source_type": "tool_result", "trust_level": "tool_output"}), "tool_result")
        self.assertEqual(RU.coarse_source({"source_type": "user", "trust_level": "authenticated_user"}), "user")
        self.assertEqual(RU.coarse_source({"source_type": "document", "trust_level": "untrusted"}), "other")

    def test_ground_truth_rejected(self):
        with self.assertRaises(AssertionError):
            RU.R1({"expected_action": "block", "requires_tool_call": True, "trust_level": "untrusted"})

    def test_handle(self):
        self.assertFalse(RU.has_structural_handle(
            {"requires_tool_call": False, "contains_sensitive_sink": False,
             "source_type": "user", "trust_level": "authenticated_user"}))
        self.assertTrue(RU.has_structural_handle(
            {"requires_tool_call": True, "contains_sensitive_sink": False,
             "source_type": "user", "trust_level": "authenticated_user"}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
