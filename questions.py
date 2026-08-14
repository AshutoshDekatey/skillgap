"""SkillGap V3: 300 deterministic, readable questions generated from 150 concept cards."""

from __future__ import annotations

import random


TRACK_LABELS = {
    "data": "SQL, Pandas & Python Data Analysis",
    "engineering": "Terraform, Microservices & SDLC",
    "finance": "Capital Markets, Payments & Private Equity",
}

SKILL_LABELS = {
    "data": {
        "sql_querying": "SQL querying",
        "sql_joins": "SQL joins",
        "sql_aggregation": "SQL aggregation",
        "sql_advanced": "Advanced SQL",
        "pandas_inspection": "Pandas inspection",
        "pandas_cleaning": "Pandas cleaning",
        "pandas_transform": "Pandas transformation",
        "python_analysis": "Python for analysis",
        "statistics": "Statistics & EDA",
        "data_quality": "Data quality",
    },
    "engineering": {
        "tf_workflow": "Terraform workflow",
        "tf_state": "Terraform state",
        "tf_configuration": "Terraform configuration",
        "tf_modules": "Terraform modules",
        "ms_architecture": "Microservice architecture",
        "ms_communication": "Service communication",
        "ms_resilience": "Resilience patterns",
        "ms_observability": "Observability",
        "sdlc_delivery": "SDLC & delivery",
        "sdlc_quality": "Testing & secure delivery",
    },
    "finance": {
        "market_equity": "Markets & equity",
        "fixed_income": "Fixed income",
        "derivatives": "Derivatives",
        "market_risk": "Market & portfolio risk",
        "payment_rails": "Payment rails",
        "payment_flow": "Payment participants",
        "payment_operations": "Payment operations & risk",
        "pe_structure": "Private-equity structure",
        "pe_lifecycle": "Private-equity lifecycle",
        "pe_returns": "Private-equity returns",
    },
}


# Each skill has five concept cards. Every card produces two differently phrased
# questions, giving 10 questions per skill and exactly 100 per learning track.
CONCEPTS = {
    "data": {
        "sql_querying": [
            ("SELECT", "Chooses the columns or expressions returned by a query."),
            ("WHERE", "Filters individual rows before grouping or aggregation."),
            ("DISTINCT", "Removes duplicate combinations from the selected result columns."),
            ("ORDER BY", "Sorts a query result by one or more expressions."),
            ("LIMIT", "Restricts the maximum number of rows returned by a query."),
        ],
        "sql_joins": [
            ("INNER JOIN", "Returns rows whose join keys match on both sides."),
            ("LEFT JOIN", "Keeps every left-side row and adds matching right-side values."),
            ("FULL OUTER JOIN", "Keeps matched rows plus unmatched rows from both sides."),
            ("CROSS JOIN", "Returns the Cartesian product of two input tables."),
            ("Self join", "Joins a table to another reference of the same table."),
        ],
        "sql_aggregation": [
            ("GROUP BY", "Combines rows into groups before calculating aggregate results."),
            ("HAVING", "Filters groups after aggregation has been calculated."),
            ("COUNT(*)", "Counts result rows regardless of whether individual columns contain NULL."),
            ("COUNT(column)", "Counts only rows where the specified column is not NULL."),
            ("Conditional aggregation", "Uses a condition inside an aggregate to calculate segmented measures."),
        ],
        "sql_advanced": [
            ("CTE", "Defines a named query result used within one larger SQL statement."),
            ("Correlated subquery", "A subquery that refers to values from the outer query."),
            ("Window function", "Calculates across related rows while retaining each row's identity."),
            ("ROW_NUMBER", "Assigns a sequential number within an ordered window partition."),
            ("LAG", "Returns a value from an earlier row in the current window."),
        ],
        "pandas_inspection": [
            ("DataFrame.head", "Displays the first rows for a quick visual inspection."),
            ("DataFrame.info", "Summarizes columns, non-null counts, dtypes and memory usage."),
            ("DataFrame.describe", "Produces descriptive statistics for supported columns."),
            ("DataFrame.shape", "Returns the DataFrame dimensions as rows and columns."),
            ("Series.nunique", "Counts distinct values in a Series."),
        ],
        "pandas_cleaning": [
            ("isna", "Creates a Boolean mask identifying missing values."),
            ("fillna", "Replaces missing values using a supplied value or rule."),
            ("dropna", "Removes rows or columns according to missing-value conditions."),
            ("duplicated", "Flags repeated rows or repeated key combinations."),
            ("to_numeric with coerce", "Converts parseable values to numbers and invalid values to NaN."),
        ],
        "pandas_transform": [
            ("loc", "Selects or updates data using row and column labels or Boolean masks."),
            ("Vectorization", "Applies array operations without writing an explicit Python row loop."),
            ("groupby", "Splits data into groups, applies calculations and combines results."),
            ("merge validate", "Checks whether merge keys satisfy an expected relationship."),
            ("pivot_table", "Creates a spreadsheet-style summary with aggregation."),
        ],
        "python_analysis": [
            ("List comprehension", "Builds a list from an iterable with a concise expression."),
            ("dict.get", "Retrieves a dictionary value while allowing a default for missing keys."),
            ("try/except", "Handles specified runtime exceptions without terminating the whole program."),
            ("Function", "Packages reusable logic behind a name, parameters and an optional return value."),
            ("Generator", "Produces values lazily instead of storing the entire sequence in memory."),
        ],
        "statistics": [
            ("Median", "The middle ordered value and a location measure resistant to extreme observations."),
            ("Standard deviation", "Measures the typical spread of observations around their mean."),
            ("Correlation", "Measures the strength and direction of association, not causation."),
            ("IQR rule", "Flags values below Q1 minus 1.5 IQR or above Q3 plus 1.5 IQR."),
            ("Sampling bias", "Occurs when the selected sample systematically differs from the target population."),
        ],
        "data_quality": [
            ("Accuracy", "Degree to which data correctly represents the real-world value."),
            ("Completeness", "Degree to which required data is present."),
            ("Consistency", "Degree to which values agree across systems, fields or rules."),
            ("Uniqueness", "Degree to which entities are represented without unintended duplication."),
            ("Validity", "Degree to which data conforms to allowed formats, ranges and business rules."),
        ],
    },
    "engineering": {
        "tf_workflow": [
            ("terraform init", "Initializes a working directory and installs required providers and modules."),
            ("terraform fmt", "Rewrites Terraform configuration into the canonical style."),
            ("terraform validate", "Checks configuration syntax and internal consistency."),
            ("terraform plan", "Previews proposed infrastructure changes without executing them."),
            ("terraform apply", "Executes the operations in an approved or newly generated plan."),
        ],
        "tf_state": [
            ("Terraform state", "Maps resource addresses in configuration to real infrastructure objects."),
            ("Remote backend", "Stores state in a shared external location instead of one local machine."),
            ("State locking", "Prevents concurrent operations from modifying the same state simultaneously."),
            ("terraform import", "Associates an existing remote object with a Terraform resource address."),
            ("moved block", "Records a resource-address change without intentionally recreating the object."),
        ],
        "tf_configuration": [
            ("Provider", "Connects Terraform resource types to an external platform API."),
            ("Resource block", "Declares an infrastructure object Terraform should manage."),
            ("Data source", "Reads information about an existing object without managing its lifecycle."),
            ("Input variable", "Allows callers to supply values without changing module source code."),
            ("Output value", "Exposes selected information from a module to callers or automation."),
        ],
        "tf_modules": [
            ("Root module", "The Terraform configuration in the directory where commands are run."),
            ("Child module", "A module called by another module to encapsulate reusable resources."),
            ("Module source", "Identifies where Terraform should retrieve a child module's code."),
            ("Version constraint", "Restricts acceptable provider or registry-module versions."),
            ("Local value", "Gives a reusable name to an expression within a module."),
        ],
        "ms_architecture": [
            ("Bounded context", "A business boundary within which a domain model has a consistent meaning."),
            ("Loose coupling", "Minimizes assumptions one service makes about another's implementation."),
            ("Database per service", "Gives each service ownership of its data rather than a shared schema."),
            ("Monolith", "Deploys multiple application capabilities together as one unit."),
            ("API gateway", "Provides a managed entry point that routes and governs client API traffic."),
        ],
        "ms_communication": [
            ("Synchronous call", "Makes the caller wait for a response before continuing its flow."),
            ("Asynchronous messaging", "Decouples sender and receiver through queued or published messages."),
            ("Idempotency", "Allows repeated processing of the same request without additional side effects."),
            ("Event-driven architecture", "Lets components publish state changes that interested consumers handle."),
            ("Service discovery", "Provides a way for services to locate available service instances."),
        ],
        "ms_resilience": [
            ("Timeout", "Stops waiting after a bounded period when a dependency does not respond."),
            ("Retry with backoff", "Retries transient failures with increasing delay between attempts."),
            ("Circuit breaker", "Temporarily blocks calls to a dependency after repeated failures."),
            ("Bulkhead", "Isolates resources so failure in one workload does not exhaust the whole system."),
            ("Saga", "Coordinates distributed local transactions with compensating actions after failure."),
        ],
        "ms_observability": [
            ("Logs", "Timestamped event records that explain what an application did."),
            ("Metrics", "Numeric time-series measurements used to monitor system behavior."),
            ("Distributed trace", "Follows one request across multiple services and operations."),
            ("Correlation ID", "A shared identifier used to connect records belonging to one request."),
            ("Health check", "Reports whether a service instance is alive or ready for traffic."),
        ],
        "sdlc_delivery": [
            ("Requirement", "States a capability or constraint the solution must satisfy."),
            ("Design review", "Evaluates a proposed solution before costly implementation decisions harden."),
            ("Version control", "Records source changes and supports collaboration, history and rollback."),
            ("Continuous integration", "Automatically builds and tests changes merged frequently into a shared repository."),
            ("Continuous delivery", "Keeps tested software in a deployable state through automated pipelines."),
        ],
        "sdlc_quality": [
            ("Unit test", "Checks a small isolated unit of behavior."),
            ("Integration test", "Checks whether multiple components work together correctly."),
            ("Contract test", "Checks whether a service interaction conforms to an agreed interface."),
            ("Regression test", "Checks that previously working behavior remains intact after change."),
            ("Shift-left security", "Introduces security checks earlier in design and development."),
        ],
    },
    "finance": {
        "market_equity": [
            ("Primary market", "Market in which issuers sell newly created securities to raise capital."),
            ("Secondary market", "Market in which investors trade securities that already exist."),
            ("Bid-ask spread", "Difference between the best displayed buying and selling prices."),
            ("Market order", "Instruction to trade promptly without guaranteeing the execution price."),
            ("Market capitalization", "Share price multiplied by the number of shares outstanding."),
        ],
        "fixed_income": [
            ("Face value", "Principal amount a bond issuer promises to repay at maturity."),
            ("Coupon", "Contractual interest payment stated for a bond."),
            ("Yield to maturity", "Discount rate equating a bond's price with promised cash flows if held to maturity."),
            ("Duration", "Measure of a bond price's sensitivity to changes in yield."),
            ("Credit spread", "Extra yield over a benchmark associated with credit and liquidity risk."),
        ],
        "derivatives": [
            ("Forward contract", "Private agreement to transact an asset later at a price fixed today."),
            ("Futures contract", "Standardized exchange-traded agreement creating future transaction obligations."),
            ("Call option", "Gives its buyer the right, not obligation, to buy at the strike price."),
            ("Put option", "Gives its buyer the right, not obligation, to sell at the strike price."),
            ("Swap", "Agreement to exchange defined cash-flow streams over time."),
        ],
        "market_risk": [
            ("Diversification", "Reduces security-specific risk by combining imperfectly correlated exposures."),
            ("Beta", "Measures an equity's sensitivity to broad market movements."),
            ("Volatility", "Measures dispersion in returns over a period."),
            ("Value at Risk", "Estimates a loss threshold for a horizon and confidence level under stated assumptions."),
            ("Liquidity risk", "Risk that a position cannot be traded quickly without significant price impact."),
        ],
        "payment_rails": [
            ("UPI", "Instant account-to-account payment system built over IMPS infrastructure in India."),
            ("IMPS", "Round-the-clock Indian service for immediate interbank electronic fund transfers."),
            ("NEFT", "Indian electronic funds-transfer system that settles eligible retail payment instructions."),
            ("RTGS", "Processes eligible transfers individually in real time on a gross basis."),
            ("NACH", "Centralized Indian system supporting recurring and bulk electronic mandates and payments."),
        ],
        "payment_flow": [
            ("Cardholder", "Person whose payment credentials are used to initiate a card transaction."),
            ("Issuer", "Financial institution that issues the payment card or account to the customer."),
            ("Acquirer", "Institution that provides card-payment acceptance to the merchant."),
            ("Card network", "Routes transaction messages and defines operating rules between participants."),
            ("Merchant", "Business that accepts payment in exchange for goods or services."),
        ],
        "payment_operations": [
            ("Authorization", "Real-time decision to approve or decline a proposed payment."),
            ("Clearing", "Exchange and calculation of transaction obligations before final settlement."),
            ("Settlement", "Final transfer of funds that discharges payment obligations."),
            ("Reconciliation", "Compares records across systems to identify breaks or mismatches."),
            ("Chargeback", "Card-payment reversal process initiated under applicable dispute rules."),
        ],
        "pe_structure": [
            ("Limited partner", "Investor that commits capital to a private-equity fund."),
            ("General partner", "Manager responsible for selecting and managing fund investments."),
            ("Committed capital", "Maximum amount an investor agrees to provide when called."),
            ("Capital call", "Request for investors to fund part of their remaining commitment."),
            ("Carried interest", "Performance allocation giving the manager a share of qualifying investment profits."),
        ],
        "pe_lifecycle": [
            ("Fundraising", "Stage in which a manager secures commitments from investors."),
            ("Due diligence", "Structured investigation of an investment's business, financial, legal and operational risks."),
            ("Leveraged buyout", "Acquisition financed with a material amount of debt alongside equity."),
            ("Value creation plan", "Operational and strategic initiatives intended to improve a portfolio company."),
            ("Exit", "Realization of an investment through sale, listing, recapitalization or another route."),
        ],
        "pe_returns": [
            ("MOIC", "Total value divided by invested capital, without considering timing."),
            ("IRR", "Annualized discount rate that makes investment cash flows have zero net present value."),
            ("DPI", "Cash distributions received by investors divided by paid-in capital."),
            ("RVPI", "Remaining unrealized fund value divided by paid-in capital."),
            ("TVPI", "Total distributed plus remaining value divided by paid-in capital."),
        ],
    },
}


def _mixed_options(correct: str, alternatives: list[str], seed: int) -> tuple[dict[str, str], str]:
    values = [correct] + alternatives[:3]
    random.Random(seed).shuffle(values)
    keys = ["A", "B", "C", "D"]
    options = dict(zip(keys, values))
    answer = next(key for key, value in options.items() if value == correct)
    return options, answer


def _build_questions() -> list[dict]:
    questions: list[dict] = []
    track_bases = {"data": 1000, "engineering": 2000, "finance": 3000}
    for track, skills in CONCEPTS.items():
        question_id = track_bases[track]
        for skill, cards in skills.items():
            terms = [term for term, _ in cards]
            definitions = [definition for _, definition in cards]
            for index, (term, definition) in enumerate(cards):
                other_definitions = definitions[index + 1:] + definitions[:index]
                options, answer = _mixed_options(definition, other_definitions, question_id)
                questions.append({
                    "id": question_id, "track": track, "skill": skill,
                    "prompt": f"Which statement best describes {term}?",
                    "options": options, "answer": answer,
                    "explanation": f"{term}: {definition}",
                    "difficulty": 1 if index < 2 else 2,
                    "diagnostic": index < 2,
                })
                question_id += 1

                other_terms = terms[index + 1:] + terms[:index]
                options, answer = _mixed_options(term, other_terms, question_id)
                questions.append({
                    "id": question_id, "track": track, "skill": skill,
                    "prompt": f"Which concept matches this description? {definition}",
                    "options": options, "answer": answer,
                    "explanation": f"The correct concept is {term}. {definition}",
                    "difficulty": 2 if index < 3 else 3,
                    "diagnostic": False,
                })
                question_id += 1
    return questions


QUESTIONS = _build_questions()
