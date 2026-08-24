from rich.console import Console

stdout = Console(highlight=False)
stderr = Console(stderr=True, highlight=False)
plain = Console(highlight=False, markup=False)
plain_error = Console(stderr=True, highlight=False, markup=False)
