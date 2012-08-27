import re
import os
import itertools
import hashlib
import urllib
import logging


import datetime
import models
import simplejson as json

from opendsa.models import Exercise, UserExercise, ProblemLog
from django.conf.urls.defaults import patterns, url
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.utils import simplejson
from django.contrib.sessions.models import Session



def make_wrong_attempt(user_data, user_exercise):
    if user_exercise and user_exercise.belongs_to(user_data):
        user_exercise.update_proficiency_model(correct=False)
        user_exercise.put()

        return user_exercise

def attempt_problem(user_data, user_exercise, problem_number, attempt_number,
    attempt_content, sha1, seed, completed, count_hints, time_taken,
    review_mode, exercise_non_summative, problem_type, ip_address):

    if user_exercise:   # and user_exercise.belongs_to(user_data):
        dt_now = datetime.datetime.now()
        print user_exercise
        exercise = user_exercise[0].exercise

       # old_graph = user_exercise.get_user_exercise_graph()

        user_exercise[0].last_done = dt_now
        user_exercise[0].seconds_per_fast_problem = exercise.seconds_per_fast_problem
        user_exercise[0].summative = exercise.summative

        #user_data.record_activity(user_exercise.last_done)

        # If a non-admin tries to answer a problem out-of-order, just ignore it
        #if problem_number != user_exercise[0].total_done + 1 and not user_util.is_current_user_developer():
            # Only admins can answer problems out of order.
         #   raise QuietException("Problem number out of order (%s vs %s) for user_id: %s submitting attempt content: %s with seed: %s" % (problem_number, user_exercise.total_done + 1, user_data.user_id, attempt_content, seed))

        if len(sha1) <= 0:
            raise Exception("Missing sha1 hash of problem content.")

        if len(seed) <= 0:
            raise Exception("Missing seed for problem content.")

        if len(attempt_content) > 500:
            raise Exception("Attempt content exceeded maximum length.")

        # Build up problem log for deferred put
        key_name=models.ProblemLog.key_for(user_data, user_exercise[0].exercise.id, problem_number)
        problem_log = models.ProblemLog(
                #key_name,   #=models.ProblemLog.key_for(user_data, user_exercise[0].exercise, problem_number),
                user=user_data, #.user,
                exercise=user_exercise[0].exercise,
                problem_number=problem_number,
                time_taken=time_taken,
                time_done=dt_now,
                count_hints=count_hints,
                hint_used=count_hints > 0,
                correct=completed and not count_hints and (attempt_number == 1),
                sha1=sha1,
                seed=seed,
                problem_type=problem_type,
                count_attempts=attempt_number,
                attempts=[attempt_content],
                ip_address=ip_address,
                review_mode=review_mode,
        )

        if exercise.summative:
            problem_log.exercise_non_summative = exercise_non_summative

        first_response = (attempt_number == 1 and count_hints == 0) or (count_hints == 1 and attempt_number == 0)

        if user_exercise[0].total_done > 0 and user_exercise[0].streak == 0 and first_response:
            bingo('hints_keep_going_after_wrong')

        just_earned_proficiency = False

        # Users can only attempt problems for themselves, so the experiment
        # bucket always corresponds to the one for this current user
        #struggling_model = StrugglingExperiment.get_alternative_for_user(
        #         user_data, current_user=True) or StrugglingExperiment.DEFAULT
        if completed:

            user_exercise[0].total_done += 1

            if problem_log.correct:

                proficient = user_data.is_proficient_at(user_exercise[0].exercise)
                explicitly_proficient = user_data.is_explicitly_proficient_at(user_exercise[0].exercise)
                suggested = user_data.is_suggested(user_exercise[0].exercise)
                problem_log.suggested = suggested

                problem_log.points_earned = points.ExercisePointCalculator(user_exercise[0], suggested, proficient)
                #user_data.add_points(problem_log.points_earned)

                # Streak only increments if problem was solved correctly (on first attempt)
                user_exercise[0].total_correct += 1
                user_exercise[0].streak += 1
                user_exercise[0].longest_streak = max(user_exercise[0].longest_streak, user_exercise[0].streak)

                user_exercise[0].update_proficiency_model(correct=True)

                bingo('struggling_problems_correct')

                if user_exercise[0].progress >= 1.0 and not explicitly_proficient:
                    bingo(['hints_gained_proficiency_all',
                           'struggling_gained_proficiency_all',
                           'homepage_restructure_gained_proficiency_all'])
                    if not user_exercise[0].has_been_proficient():
                        bingo('hints_gained_new_proficiency')

                    if user_exercise.history_indicates_struggling(struggling_model):
                        bingo('struggling_gained_proficiency_post_struggling')

                    user_exercise[0].set_proficient(user_data)
                    user_data.reassess_if_necessary()

                    just_earned_proficiency = True
                    problem_log.earned_proficiency = True

#            util_badges.update_with_user_exercise(
#                user_data,
#                user_exercise,
#                include_other_badges=True,
#                action_cache=last_action_cache.LastActionCache.get_cache_and_push_problem_log(user_data, problem_log))

            # Update phantom user notifications
#            util_notify.update(user_data, user_exercise)

#            bingo([
#                'hints_problems_done',
#                'struggling_problems_done',
#                'homepage_restructure_problems_done',
#            ])

        else:
            # Only count wrong answer at most once per problem
            if first_response:
                user_exercise[0].update_proficiency_model(correct=False)
#                bingo(['hints_wrong_problems', 'struggling_problems_wrong'])

#            if user_exercisei[0].is_struggling(struggling_model):
#                bingo('struggling_struggled_binary')

        # If this is the first attempt, update review schedule appropriately
        if attempt_number == 1:
            user_exercise[0].schedule_review(completed)

#        user_exercise_graph = models.UserExerciseGraph.get_and_update(user_data, user_exercise)

#        goals_updated = GoalList.update_goals(user_data,
#            lambda goal: goal.just_did_exercise(user_data, user_exercise,
#                just_earned_proficiency))

        # Bulk put
#        db.put([user_data, user_exercise, user_exercise_graph.cache])

        # Defer the put of ProblemLog for now, as we think it might be causing hot tablets
        # and want to shift it off to an automatically-retrying task queue.
        # http://ikaisays.com/2011/01/25/app-engine-datastore-tip-monotonically-increasing-values-are-bad/
#        deferred.defer(models.commit_problem_log, problem_log,
#                       _queue="problem-log-queue",
#                       _url="/_ah/queue/deferred_problemlog")

#        if user_data is not None and user_data.coaches:
#            # Making a separate queue for the log summaries so we can clearly see how much they are getting used
#            deferred.defer(models.commit_log_summary_coaches, problem_log, user_data.coaches,
#                       _queue="log-summary-queue",
#                       _url="/_ah/queue/deferred_log_summary")
        problem_log.save()
        return user_exercise[0]      #, user_exercise_graph, goals_updated

