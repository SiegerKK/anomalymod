import tempfile
import unittest
from pathlib import Path

from tools import audit_trade_configs as audit


class AuditTradeConfigsTests(unittest.TestCase):
    def test_windows_include_and_physical_tiers(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            trade = root / "gamedata/configs/items/trade"
            presets = trade / "presets"
            presets.mkdir(parents=True)
            (presets / "trade_presets.ltx").write_text("[base_stock]\nbandage = 1, 0.5\n", encoding="utf-8")
            (trade / "trade_test.ltx").write_text(
                '#include "presets\\trade_presets.ltx"\n'
                '[trader]\nbuy_supplies = supplies_2\n\n'
                '[supplies_1]:base_stock\nammo_9x18_fmj = 2, 0.25\n\n'
                '[supplies_2]:supplies_1\nammo_9x18_pmm = 3, 0.75\n',
                encoding="utf-8",
            )
            (trade / "mod_trade_test_weekly_stock.ltx").write_text(
                '![trader]\nbuy_supplies = supplies_weekly\n\n@[supplies_weekly]:supplies_2\n',
                encoding="utf-8",
            )
            rows, errors = audit.audit(audit.load_profiles(root, None))
            self.assertEqual(errors, [])
            tiers = {row["item"]: row["original_tiers"] for row in rows}
            self.assertEqual(tiers["ammo_9x18_fmj"], "supplies_1")
            self.assertEqual(tiers["ammo_9x18_pmm"], "supplies_2")
            self.assertEqual(tiers["bandage"], "supplies_weekly")

    def test_invalid_supply_values_are_errors(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            trade = root / "gamedata/configs/items/trade"
            trade.mkdir(parents=True)
            (trade / "trade_bad.ltx").write_text(
                '[trader]\nbuy_supplies = supplies_weekly\n\n'
                '[supplies_1]\nbad_qty = 0, 0.5\nbad_prob = 1, 2\nbad_extra = 1, 0.5, 7\n\n'
                '@[supplies_weekly]:supplies_1\n',
                encoding="utf-8",
            )
            rows, errors = audit.audit(audit.load_profiles(root, None))
            self.assertTrue(rows)
            self.assertGreaterEqual(len(errors), 3)


if __name__ == "__main__":
    unittest.main()
