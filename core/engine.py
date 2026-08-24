"""Execution engine for orchestrating skill runs"""

import time
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import copy

from config import MAX_SKILL_EXECUTION_TIME, VERBOSITY
from core.context import Context
from core.registry import Registry
from core.scoring_engine import ScoringEngine
from ai.planner import choose_skill, choose_skill_batch

logger = logging.getLogger(__name__)


class Engine:
    """Autonomous execution engine (sequential + parallel safe mode)"""

    def __init__(self, registry: Registry):
        self.registry = registry
        self.execution_count = 0
        self._merge_lock = asyncio.Lock()  # Fix #4: lock for thread-safe merges

    # -----------------------------
    # MAIN AUTONOMOUS LOOP
    # -----------------------------
    def run(self, context: Context) -> Context:
        logger.info(f"Starting autonomous analysis: {context.target}")
        logger.info(f"Available skills: {self.registry.list_skills()}")

        max_iterations = 50
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # decide mode dynamically
            mode = "parallel" if len(context.findings) < 3 else "sequential"

            if VERBOSITY >= 2:
                logger.debug(f"[Cycle {iteration}] Mode: {mode}")

            # -----------------------------
            # PARALLEL MODE
            # -----------------------------
            if mode == "parallel":
                skills = choose_skill_batch(context, self.registry)

                if not skills:
                    break

                logger.info(f"[PARALLEL BATCH] {skills}")

                context = asyncio.run(self.run_parallel(skills, context))

            # -----------------------------
            # SEQUENTIAL MODE
            # -----------------------------
            else:
                skill_name = choose_skill(context, self.registry)

                if skill_name in ["stop", "report", None]:
                    break

                skill = self.registry.get(skill_name)

                if not skill:
                    context.skipped_skills.append(skill_name)
                    continue

                try:
                    start = time.time()
                    context = self._execute_skill(skill, context)
                    duration = time.time() - start

                    context.executed_skills.append(skill_name)
                    context.add_execution(skill_name, duration, True)
                    self.execution_count += 1  # Fix #3: increment counter

                    if duration > MAX_SKILL_EXECUTION_TIME:
                        logger.warning(f"{skill_name} exceeded time limit")

                except Exception as e:
                    logger.error(f"{skill_name} failed: {str(e)}", exc_info=True)
                    context.add_error(skill_name, str(e))

            if len(context.findings) > 15:
                logger.info("Stopping: sufficient intelligence gathered")
                break

        logger.info(
            f"Autonomous run complete | "
            f"Skills: {self.execution_count} | "
            f"Findings: {len(context.findings)}"
        )

        # Score all findings in-place; ScoringEngine mutates Finding.score and sorts
        logger.info("Scoring findings...")
        scorer = ScoringEngine()
        if context.findings:
            scorer.score_all(context.findings)  # mutates in-place, returns same list sorted
        logger.info(f"Scored {len(context.findings)} findings")

        # Always build the final report, regardless of why the loop stopped
        # (explicit "report" signal, "stop" signal, or max_iterations reached).
        # Without this, context.report stays {} even after a full run.
        report_skill = self.registry.get("report")
        if report_skill:
            try:
                context = self._execute_skill(report_skill, context)
                logger.info("Report generated")
            except Exception as e:
                logger.error(f"Report generation failed: {str(e)}", exc_info=True)
                context.add_error("report", str(e))
        else:
            logger.warning("No 'report' skill registered — context.report left empty")

        return context

    # -----------------------------
    # SINGLE SKILL EXECUTION
    # -----------------------------
    def _execute_skill(self, skill: dict, context: Context) -> Context:
        result = skill["run"](context)

        if not isinstance(result, Context):
            raise TypeError("Skill must return Context")

        return result

    # -----------------------------
    # ⚡ SAFE PARALLEL EXECUTION ENGINE
    # -----------------------------
    async def run_parallel(self, skills: list[str], context: Context) -> Context:
        """Parallel execution with isolation safety"""

        executor = ThreadPoolExecutor(max_workers=5)
        loop = asyncio.get_running_loop()

        async def run_one(skill_name: str):
            skill = self.registry.get(skill_name)

            if not skill:
                context.skipped_skills.append(skill_name)
                return

            start = time.time()

            # 🔒 ISOLATE CONTEXT PER SKILL
            local_context = copy.deepcopy(context)

            try:
                await loop.run_in_executor(
                    executor,
                    skill["run"],
                    local_context
                )

                duration = time.time() - start

                # Fix #4: acquire lock before merging to prevent race conditions
                async with self._merge_lock:
                    self._merge_context(context, local_context)
                    context.executed_skills.append(skill_name)
                    context.add_execution(skill_name, duration, True)
                    self.execution_count += 1  # Fix #3: increment in parallel path too

                logger.info(f"[PARALLEL] {skill_name} done")

            except Exception as e:
                duration = time.time() - start
                async with self._merge_lock:  # Fix #4: lock error writes too
                    context.add_error(skill_name, str(e))
                    context.add_execution(skill_name, duration, False)

                logger.error(f"[PARALLEL] {skill_name} failed: {str(e)}")

        await asyncio.gather(*[run_one(s) for s in skills])

        return context

    # -----------------------------
    # CONTEXT MERGER
    # -----------------------------
    def _merge_context(self, main: Context, local: Context):
        """Safely merge results from parallel execution"""

        for s in local.subdomains:
            if s not in main.subdomains:
                main.subdomains.append(s)

        for e in local.endpoints:
            if e not in main.endpoints:
                main.endpoints.append(e)

        for svc in local.services:
            if svc not in main.services:
                main.services.append(svc)

        # merge findings (avoid duplicates)
        for f in local.findings:
            if f not in main.findings:
                main.findings.append(f)

        # Fix #6: deduplicate errors on merge
        for err in local.errors:
            if err not in main.errors:
                main.errors.append(err)
