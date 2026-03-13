from typing import Any, Mapping, Sequence
import jmespath
from functools import partial


bet9ja_search_string = ('D.E[*].{"match": DS, '
                        '"league": GN, '
                        '"time": STARTDATE, '
                        '"league_id": GID, '
                        '"match_id": ID, '
                        '"home": O.S_1X2_1, '
                        '"draw": O.S_1X2_X, '
                        '"away": O.S_1X2_2, '
                        '"home_or_draw": O.S_DC_1X, '
                        '"home_or_away": O.S_DC_12, '
                        '"draw_or_away": O.S_DC_X2, '
                        '"over_0_5": O."S_OU@0.5_O", '
                        '"under_0_5": O."S_OU@0.5_U", '
                        '"over_1_5": O."S_OU@1.5_O", '
                        '"under_1_5": O."S_OU@1.5_U", '
                        '"over_2_5": O."S_OU@2.5_O", '
                        '"under_2_5": O."S_OU@2.5_U", '
                        '"over_3_5": O."S_OU@3.5_O", '
                        '"under_3_5": O."S_OU@3.5_U", '
                        '"over_4_5": O."S_OU@4.5_O", '
                        '"under_4_5": O."S_OU@4.5_U", '
                        '"over_5_5": O."S_OU@5.5_O", '
                        '"under_5_5": O."S_OU@5.5_U", '
                        '"over_6_5": O."S_OU@6.5_O", '
                        '"under_6_5": O."S_OU@6.5_U", '
                        '"btts_yes": O.S_GGNG_Y, '
                        '"btts_no": O.S_GGNG_N '
                        '}')

# Bet9ja corners over/under (GROUPMARKETID=216 "Main Corner")
bet9ja_corners_search_string = ('D.E[*].{"match_id": ID, '
                                '"corners_over_6_5": O."S_OUCORNERS@6.5_O", '
                                '"corners_under_6_5": O."S_OUCORNERS@6.5_U", '
                                '"corners_over_7_5": O."S_OUCORNERS@7.5_O", '
                                '"corners_under_7_5": O."S_OUCORNERS@7.5_U", '
                                '"corners_over_8_5": O."S_OUCORNERS@8.5_O", '
                                '"corners_under_8_5": O."S_OUCORNERS@8.5_U", '
                                '"corners_over_9_5": O."S_OUCORNERS@9.5_O", '
                                '"corners_under_9_5": O."S_OUCORNERS@9.5_U", '
                                '"corners_over_10_5": O."S_OUCORNERS@10.5_O", '
                                '"corners_under_10_5": O."S_OUCORNERS@10.5_U", '
                                '"corners_over_11_5": O."S_OUCORNERS@11.5_O", '
                                '"corners_under_11_5": O."S_OUCORNERS@11.5_U", '
                                '"corners_over_12_5": O."S_OUCORNERS@12.5_O", '
                                '"corners_under_12_5": O."S_OUCORNERS@12.5_U", '
                                '"corners_over_13_5": O."S_OUCORNERS@13.5_O", '
                                '"corners_under_13_5": O."S_OUCORNERS@13.5_U" '
                                '}')

# Bet9ja Asian handicap (GROUPMARKETID=S_AH "Asian Handicap")
bet9ja_asian_handicap_search_string = ('D.E[*].{"match_id": ID, '
                                       '"ah_minus_2_5_1": O."S_AH@-2.5_1", '
                                       '"ah_minus_2_5_2": O."S_AH@-2.5_2", '
                                       '"ah_minus_2_1": O."S_AH@-2_1", '
                                       '"ah_minus_2_2": O."S_AH@-2_2", '
                                       '"ah_minus_1_5_1": O."S_AH@-1.5_1", '
                                       '"ah_minus_1_5_2": O."S_AH@-1.5_2", '
                                       '"ah_minus_1_1": O."S_AH@-1_1", '
                                       '"ah_minus_1_2": O."S_AH@-1_2", '
                                       '"ah_minus_0_75_1": O."S_AH@-0.75_1", '
                                       '"ah_minus_0_75_2": O."S_AH@-0.75_2", '
                                       '"ah_minus_0_5_1": O."S_AH@-0.5_1", '
                                       '"ah_minus_0_5_2": O."S_AH@-0.5_2", '
                                       '"ah_minus_0_25_1": O."S_AH@-0.25_1", '
                                       '"ah_minus_0_25_2": O."S_AH@-0.25_2", '
                                       '"ah_0_1": O."S_AH@0_1", '
                                       '"ah_0_2": O."S_AH@0_2", '
                                       '"ah_plus_0_25_1": O."S_AH@0.25_1", '
                                       '"ah_plus_0_25_2": O."S_AH@0.25_2", '
                                       '"ah_plus_0_5_1": O."S_AH@0.5_1", '
                                       '"ah_plus_0_5_2": O."S_AH@0.5_2", '
                                       '"ah_plus_0_75_1": O."S_AH@0.75_1", '
                                       '"ah_plus_0_75_2": O."S_AH@0.75_2", '
                                       '"ah_plus_1_1": O."S_AH@1_1", '
                                       '"ah_plus_1_2": O."S_AH@1_2", '
                                       '"ah_plus_1_5_1": O."S_AH@1.5_1", '
                                       '"ah_plus_1_5_2": O."S_AH@1.5_2", '
                                       '"ah_plus_2_1": O."S_AH@2_1", '
                                       '"ah_plus_2_2": O."S_AH@2_2", '
                                       '"ah_plus_2_5_1": O."S_AH@2.5_1", '
                                       '"ah_plus_2_5_2": O."S_AH@2.5_2" '
                                       '}')

betking_search_string = ('AreaMatches[0].Items[*].{"match": ItemName, '
                         '"league": TournamentName, '
                         '"time": ItemDate, '
                         '"league_id": CategoryId, '
                         '"match_id": ItemID, '
                         '"home": OddsCollection[0].MatchOdds[0].Outcome.OddOutcome '
                         '"draw": OddsCollection[0].MatchOdds[1].Outcome.OddOutcome '
                         '"away": OddsCollection[0].MatchOdds[2].Outcome.OddOutcome '
                         '"home_or_draw": OddsCollection[1].MatchOdds[0].Outcome.OddOutcome '
                         '"home_or_away": OddsCollection[1].MatchOdds[1].Outcome.OddOutcome '
                         '"draw_or_away": OddsCollection[1].MatchOdds[2].Outcome.OddOutcome '
                         '}')

# nairabet_search_string = ('data[*].{"match": eventName, '
#                           '"league": category3Name, '
#                           '"time": eventStart, '
#                           '"league_id": category3Id, '
#                           '"match_id": eventId, '
#                           '"home": eventGames[0].outcomes[0].outcomeOdds '
#                           '"draw": eventGames[0].outcomes[1].outcomeOdds '
#                           '"away": eventGames[0].outcomes[2].outcomeOdds '
#                           '"home_or_draw": eventGames[1].outcomes[0].outcomeOdds '
#                           '"home_or_away": eventGames[1].outcomes[1].outcomeOdds '
#                           '"draw_or_away": eventGames[1].outcomes[2].outcomeOdds '
#                           '}')

nairabet_search_string = 'data.categories[0].competitions[0].events[*].{ ' \
                         '"match": join( \' - \', eventNames), ' \
                         '"time": startTime ' \
                         '"match_id": id, ' \
                         '"home": markets[0].outcomes[0].value, ' \
                         '"draw": markets[0].outcomes[1].value, ' \
                         '"away": markets[0].outcomes[2].value ' \
                         '}'

nairabet_league_search_string = 'data.categories[0].competitions[*].{ ' \
                                '"league": name, ' \
                                '"league_id": id ' \
                                '}'


def validator(json, search_string) -> Sequence[Mapping[Any, Any]]:

    """
    An helper function that cleans the endpoint returned json

    Args:
        json (dict): The json returned from the endpoint

    Returns:
        json (list(dict)): A list of dicts containing the league data in a more human readable format
    """

    expression = jmespath.compile(search_string)
    return expression.search(json)


bet9ja_validator = partial(validator, search_string=bet9ja_search_string)
bet9ja_corners_validator = partial(validator, search_string=bet9ja_corners_search_string)
bet9ja_asian_handicap_validator = partial(validator, search_string=bet9ja_asian_handicap_search_string)
betking_validator = partial(validator, search_string=betking_search_string)
nairabet_validator = partial(validator, search_string=nairabet_search_string)
nairabet_league_validator = partial(validator, search_string=nairabet_league_search_string)


def merge_bet9ja_markets(main_results, *extra_results_list):
    """Merge extra market data (corners, Asian handicap) into main results by match_id.

    Each extra_results list contains dicts with 'match_id' plus market-specific fields.
    Fields with None values from extra results are excluded from the merge.
    Events in main_results that have no corresponding extra data are left unchanged.
    """
    if not main_results:
        return main_results

    # Index main results by match_id for O(1) lookup
    main_by_id = {match['match_id']: match for match in main_results if match.get('match_id')}

    for extra_results in extra_results_list:
        if not extra_results:
            continue
        for extra in extra_results:
            mid = extra.get('match_id')
            if mid and mid in main_by_id:
                # Merge non-None fields (skip match_id itself)
                for key, value in extra.items():
                    if key != 'match_id' and value is not None:
                        try:
                            value = float(value)
                        except (ValueError, TypeError):
                            pass
                        main_by_id[mid][key] = value

    return main_results
