class HumanCheckAgent:
    async def run(self, verified_data):
        """
        Optionally implements manual validation or output parsing logic.
        Does not require any environment variables.
        Args:
            verified_data: Data already validated by automatic agents.
        Returns:
            The input data, unchanged.
        """
        return verified_data
