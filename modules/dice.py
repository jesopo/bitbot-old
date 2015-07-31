import random, re

REGEX_DICE = re.compile("^(\d+)?d(\d+)((?:[-*+]\d+)*)$", re.I)
REGEX_MODIFIERS = re.compile("([-*+])(\d+)")

class Module(object):
    def __init__(self, bot):
        bot.events.on("received").on("command").on("roll").hook(
            self.roll, min_args=1, help=
            "Roll a dice using d&d notation.")
    
    def roll(self, event):
        match = re.match(REGEX_DICE, event["args_split"][0])
        if not match:
            return "Provided dice notation is invalid."
        reason = " ".join(event["args_split"][1:])
        if reason:
            reason = "for %s" % reason
        dice_amount = 1 if not match.group(1) else int(match.group(1))
        if dice_amount > 10:
            return "The maximum number of dice is 10."
        sides = int(match.group(2))
        if sides > 20:
            return "The maximum number of sides is 20."
        results = []
        for i in range(dice_amount):
            results.append(random.randint(1, sides))
        modifiers = 0
        crit_modifiers = 0
        for modifier_match in re.finditer(REGEX_MODIFIERS, match.group(3)):
            symbol = modifier_match.group(1)
            modifier = int(modifier_match.group(2))
            if symbol == "*":
                if crit_modifiers:
                    modifier -= 1
                crit_modifiers += modifier
            elif symbol == "-":
                modifiers -= modifier
            elif symbol == "+":
                modifiers += modifier
        if not crit_modifiers:
            crit_modifiers = 1
        final_results = []
        for result in results:
            result += modifiers
            result *= crit_modifiers
            final_results.append(str(result))
        return "%s rolls %s %s and gets %s" % (event["sender"].nickname, event[
            "args_split"][0], reason, ", ".join(final_results))