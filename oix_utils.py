import logging
from collections import defaultdict
import bz2
from gensim.models.doc2vec import TaggedDocument


def remove_duplicates(route):
    if len(route) <= 1:
        return route
    non_dup_route = [route[0]]
    for asn in route[1:]:
        if asn != non_dup_route[-1]:
            non_dup_route.append(asn)
    return non_dup_route


def generate_routes_from_file_handler(f, remove_dup=True, remove_first=False, by_vantage=False, by_ap=False, by_asn=False,
                                      mode=None, test_limit=None, asn_list=None, ap_list=None, old_ver=False):
    counter = 0
    if remove_first:
        start_ind = 7
    else:
        start_ind = 6

    last_ap = None

    if by_vantage:
        routes_by_vantage = defaultdict(list)
        for i, line in enumerate(f):
            line = line.split()
            if len(line) > 0 and line[0] == '*':
                if mode != 'specific' or (asn_list and [asn for asn in asn_list if (asn in line)]) \
                        or (ap_list and [ap for ap in ap_list if (ap == line[1])]):
                    if old_ver:
                        if '0' not in line:
                            continue
                        start_ind = line.index('0') + 1
                    if remove_dup:
                        routes_by_vantage[line[start_ind]].append(remove_duplicates(line[start_ind:-1]))
                    else:
                        routes_by_vantage[line[start_ind]].append(line[start_ind:-1])
                    counter += 1
            if mode == 'test' and counter >= test_limit:
                break
        return routes_by_vantage, counter

    elif by_ap:
        routes_by_ap = defaultdict(list)
        for i, line in enumerate(f):
            line = line.split()
            if len(line) > 0 and line[0] == '*':
                if mode != 'specific' or (asn_list and [asn for asn in asn_list if (asn in line)]) \
                        or (ap_list and [ap for ap in ap_list if (ap == line[1])]):
                    if old_ver:
                        if '0' not in line:
                            last_ap = line[1]
                            continue
                        start_ind = line.index('0') + 1
                        if '.' in line[2]:
                            last_ap = line[1]
                        ap = last_ap
                    else:
                        ap = line[1]
                    if remove_dup:
                        routes_by_ap[ap].append(remove_duplicates(line[start_ind:-1]))
                    else:
                        routes_by_ap[ap].append(line[start_ind:-1])
                    counter += 1
            if mode == 'test' and counter >= test_limit:
                break
        return routes_by_ap, counter

    elif mode == 'specific' and len(ap_list) == 1:
        routes = []
        ap = ap_list[0]
        apply = True
        previous = None
        for i, line in enumerate(f):
            if apply or previous == ap:
                line = line.split()
                if len(line) > 0:
                    if old_ver:
                        if '0' not in line:
                            last_ap = line[1]
                            continue
                        start_ind = line.index('0') + 1
                        if '.' in line[2]:
                            last_ap = line[1]
                        cur_ap = last_ap
                    else:
                        cur_ap = line[1]
                    if ap == cur_ap:
                        if remove_dup:
                            routes.append(remove_duplicates(line[start_ind:-1]))
                        else:
                            routes.append(line[start_ind:-1])
                        counter += 1
                        previous = line[1]
            else:
                break
        return routes, counter

    elif by_asn:
        routes_by_asn = defaultdict(list)
        for i, line in enumerate(f):
            line = line.split()
            if len(line) > 0 and line[0] == '*':
                if mode != 'specific' or (asn_list and [asn for asn in asn_list if (asn in line)]) \
                        or (ap_list and [ap for ap in ap_list if (ap == line[1])]):
                    if old_ver:
                        if '0' not in line:
                            continue
                        start_ind = line.index('0') + 1
                    if remove_dup:
                        routes_by_asn[line[-2]].append(remove_duplicates(line[start_ind:-1]))
                    else:
                        routes_by_asn[line[-2]].append(line[start_ind:-1])
                    counter += 1
            if mode == 'test' and counter >= test_limit:
                break
        return routes_by_asn, counter

    else:
        routes = []
        for i, line in enumerate(f):
            line = line.split()
            if len(line) > 0 and line[0] == '*':
                if mode != 'specific' or (asn_list and [asn for asn in asn_list if (asn in line)]) \
                        or (ap_list and [ap for ap in ap_list if (ap == line[1])]):
                    if old_ver:
                        if '0' not in line:
                            continue
                        start_ind = line.index('0') + 1
                    if remove_dup:
                        routes.append(remove_duplicates(line[start_ind:-1]))
                    else:
                        routes.append(line[start_ind:-1])
                    counter += 1
            if mode == 'test' and counter >= test_limit:
                break
        return routes, counter


def get_routes_from_oix(oix_path, dt=None, remove_dup=True, remove_first=False, by_vantage=False, by_ap=False, by_asn=False, 
                        mode=None, test_limit=None,
                        asn_list=None, ap_list=None):
    if oix_path == '-':
        logging.critical(('There are no routes for dt', dt))
        raise Exception
    else:
        logging.info(("Start extracting routes from ", oix_path))
        if oix_path.endswith('.bz2'):
            with bz2.open(oix_path, "rt") as f:
                routes_by_vantage, counter = generate_routes_from_file_handler(f, remove_dup=remove_dup, remove_first=remove_first,
                                                                               by_vantage=by_vantage, old_ver='.dat' in oix_path,
                                                                               by_ap=by_ap, mode=mode, by_asn = by_asn,
                                                                               test_limit=test_limit,
                                                                               asn_list=asn_list, ap_list=ap_list)
        else:
            with open(oix_path) as f:
                routes_by_vantage, counter = generate_routes_from_file_handler(f, remove_dup=remove_dup, remove_first=remove_first,
                                                                               by_vantage=by_vantage,  old_ver='.dat' in oix_path,
                                                                               by_ap=by_ap, mode=mode, by_asn=by_asn,
                                                                               test_limit=test_limit,
                                                                               asn_list=asn_list, ap_list=ap_list)

        logging.info(("Extracted", counter, "routes from ", oix_path))
        return routes_by_vantage


def get_ap_list_from_oix(oix_path, dt=None, mode=None, test_limit=None, asn_list=None, ap_list=None, old_ver=False):
    def get_ap_set_from_file_handler(f, mode=mode, test_limit=test_limit, asn_list=asn_list, ap_list=ap_list):
        ap_set = set()
        counter = 0
        last_ap = None
        for i, line in enumerate(f):
            line = line.split()
            if len(line) > 0 and line[0] == '*':
                if mode != 'specific' or (asn_list and [asn for asn in asn_list if (asn in line)]) \
                        or (ap_list and [ap for ap in ap_list if (ap == line[1])]):
                    if old_ver:
                        if '.' in line[2] or '0' not in line:
                            last_ap = line[1]
                        ap = last_ap
                    else:
                        ap = line[1]
                    ap_set.add(ap)
                    counter += 1
            if mode == 'test' and counter >= test_limit:
                break
        return ap_set

    if oix_path == '-':
        logging.critical(('There are no routes for dt', dt))
        raise Exception
    else:
        logging.info(("Start extracting routes from ", oix_path))
        if oix_path.endswith('.bz2'):
            with bz2.open(oix_path, "rt") as f:
                ap_set = get_ap_set_from_file_handler(f, mode=mode, test_limit=test_limit,
                                                      asn_list=asn_list, ap_list=ap_list)
        else:
            with open(oix_path) as f:
                ap_set = get_ap_set_from_file_handler(f, mode=mode, test_limit=test_limit,
                                                      asn_list=asn_list, ap_list=ap_list)

        logging.info(("Extracted", len(ap_set), "aps from ", oix_path))
        return list(ap_set)


def get_asn_aps_dict_from_oix(oix_path, dt=None, mode=None, test_limit=None, asn_list=None, ap_list=None, old_ver=False):
    def get_asn_aps_dict_from_file_handler(f, mode=mode, test_limit=test_limit, asn_list=asn_list, ap_list=ap_list):
        asn_aps_dict = defaultdict(set)
        ap_asn_dict = dict()
        counter = 0
        last_ap = None
        for i, line in enumerate(f):
            line = line.split()
            if len(line) > 0 and line[0] == '*':
                if mode != 'specific' or (asn_list and [asn for asn in asn_list if (asn in line)]) \
                        or (ap_list and [ap for ap in ap_list if (ap == line[1])]):
                    if old_ver:
                        if '.' in line[2] or '0' not in line:
                            last_ap = line[1]
                        ap = last_ap
                    else:
                        ap = line[1]
                    asn_aps_dict[line[-2]].add(ap)
                    ap_asn_dict[ap] = line[-2]
                    counter += 1
            if mode == 'test' and counter >= test_limit:
                break
        return dict(asn_aps_dict), ap_asn_dict, counter

    if oix_path == '-':
        logging.critical(('There are no routes for dt', dt))
        raise Exception
    else:
        logging.info(("Start extracting routes from ", oix_path))
        if oix_path.endswith('.bz2'):
            with bz2.open(oix_path, "rt") as f:
                asn_aps_dict, ap_asn_dict, counter = get_asn_aps_dict_from_file_handler(f, mode=mode, test_limit=test_limit,
                                                      asn_list=asn_list, ap_list=ap_list)
        else:
            with open(oix_path) as f:
                asn_aps_dict, ap_asn_dict, counter = get_asn_aps_dict_from_file_handler(f, mode=mode, test_limit=test_limit,
                                                      asn_list=asn_list, ap_list=ap_list)

        logging.info(("Extracted ", counter, " aps and ", len(asn_aps_dict), " asns from ", oix_path))
        return dict(asn_aps_dict), ap_asn_dict


def generate_tagged_routes_from_oix(oix_path, dt=None, remove_dup=False, remove_first=False, mode=None, test_limit=None, asn_list=None, ap_list=None, old_ver=False):
    def generate_tagged_routes_from_file_handler(f, remove_dup=remove_dup, remove_first=remove_first, mode=mode, test_limit=test_limit,
                                                 asn_list=asn_list, ap_list=ap_list):
        ap_set = set()
        tagged_routes = []
        counter = 0
        last_ap = None
        if remove_first:
            start_ind = 7
        else:
            start_ind = 6
        for i, line in enumerate(f):
            line = line.split()
            if len(line) > 0 and line[0] == '*':
                if mode != 'specific' or (asn_list and [asn for asn in asn_list if (asn in line)]) \
                        or (ap_list and [ap for ap in ap_list if (ap == line[1])]):
                    if old_ver:
                        if '0' not in line:
                            last_ap = line[1]
                            continue
                        start_ind = line.index('0') + 1
                        if '.' in line[2]:
                            last_ap = line[1]
                        ap = last_ap
                    else:
                        ap = line[1]
                    if remove_dup:
                        tagged_routes.append(TaggedDocument(remove_duplicates(line[start_ind:-1]), [ap]))
                    else:
                        tagged_routes.append(TaggedDocument(line[start_ind:-1], [ap]))
                    ap_set.add(ap)
                    counter += 1
            if mode == 'test' and counter >= test_limit:
                break
        return tagged_routes, ap_set, counter

    if oix_path == '-':
        logging.critical(('There are no routes for dt', dt))
        raise Exception
    else:
        logging.info(("Start generating tagged routes from ", oix_path))
        if oix_path.endswith('.bz2'):
            with bz2.open(oix_path, "rt") as f:
                tagged_routes, ap_set, counter = generate_tagged_routes_from_file_handler(f, remove_dup=remove_dup, remove_first=remove_first, mode=mode, test_limit=test_limit,
                                                      asn_list=asn_list, ap_list=ap_list)
        else:
            with open(oix_path) as f:
                tagged_routes, ap_set, counter = generate_tagged_routes_from_file_handler(f, remove_dup=remove_dup, remove_first=remove_first, mode=mode, test_limit=test_limit,
                                                      asn_list=asn_list, ap_list=ap_list)

        logging.info(("Extracted", len(ap_set), "aps from ", oix_path))
        logging.info(("Extracted", counter, "routes from ", oix_path))
        return tagged_routes, list(ap_set)


def generate_diff_same_changed_dict_routes_from_prev_current_dicts(prev_dict, cur_dict):
    diff_dict = dict()
    same_dict = dict()
    changed_dict = dict()

    for ap, routes in cur_dict.items():
        routes = set(tuple(i) for i in routes)
        prev_routes = set(tuple(i) for i in prev_dict.get(ap, []))

        diff_routes = list(routes - prev_routes)
        if len(diff_routes) > 0:
            diff_dict[ap] = diff_routes

        same_routes = list(routes & prev_routes)
        if len(same_routes) > 0:
            same_dict[ap] = same_routes

        changed_routes = list(prev_routes - routes)
        if len(changed_routes) > 0:
            changed_dict[ap] = changed_routes

    logging.info("Generated diff_dict, same_dict, changed_dict")
    return diff_dict, same_dict, changed_dict


def generate_tagged_routes_from_dict_routes(dict_routes):
    tagged_routes = []
    for ap, routes in dict_routes.items():
        for route in routes:
            tagged_routes.append(TaggedDocument(route, [ap]))

    logging.info("Generated tagged_routes from dict_routes")
    return tagged_routes


# def generate_diff_same_tagged_routes_from_oix(cur_oix_path, prev_oix_path, dt=None, remove_dup=False, remove_first=False, mode=None, test_limit=None, asn_list=None, ap_list=None):
#     def generate_diff_same_tagged_routes_from_file_handler(cur_f, prev_f, remove_dup=remove_dup, remove_first=remove_first, mode=mode, test_limit=test_limit,
#                                                  asn_list=asn_list, ap_list=ap_list):
#         ap_set = set()
#         diff_tagged_routes = []
#         same_tagged_routes = []
#         counter = 0
#         if remove_first:
#             start_ind = 7
#         else:
#             start_ind = 6
#         for i, line in enumerate(cur_f):
#             cur_line = line.split()
#             prev_line = prev_f.readline()
#             if len(cur_line) > 0 and cur_line[0] == '*':
#                 if mode != 'specific' or (asn_list and [asn for asn in asn_list if (asn in cur_line)]) \
#                         or (ap_list and [ap for ap in ap_list if (ap == cur_line[1])]):
#                     if remove_dup:
#                         if line == prev_line:
#                             same_tagged_routes.append(TaggedDocument(remove_duplicates(cur_line[start_ind:-1]), [cur_line[1]]))
#                         else:
#                             diff_tagged_routes.append(TaggedDocument(remove_duplicates(cur_line[start_ind:-1]), [cur_line[1]]))
#                     else:
#                         if line == prev_line:
#                             same_tagged_routes.append(TaggedDocument(cur_line[start_ind:-1], [cur_line[1]]))
#                         else:
#                             diff_tagged_routes.append(TaggedDocument(cur_line[start_ind:-1], [cur_line[1]]))
#                     ap_set.add(cur_line[1])
#                     counter += 1
#             if mode == 'test' and counter >= test_limit:
#                 break
#         return diff_tagged_routes, same_tagged_routes, ap_set, counter
#
#     if cur_oix_path == '-' or prev_oix_path == '-':
#         logging.critical(('There are no routes for dt', dt))
#         raise Exception
#     else:
#         logging.info(("Start generating diff and same tagged routes from ", cur_oix_path))
#         if cur_oix_path.endswith('.bz2'):
#             with bz2.open(cur_oix_path, "rt") as cur_f:
#                 with bz2.open(prev_oix_path, "rt") as prev_f:
#                     diff_tagged_routes, same_tagged_routes, ap_set, counter = generate_diff_same_tagged_routes_from_file_handler(cur_f, prev_f, remove_dup=remove_dup, remove_first=remove_first, mode=mode, test_limit=test_limit,
#                                                       asn_list=asn_list, ap_list=ap_list)
#         else:
#             with open(cur_oix_path) as cur_f:
#                 with open(prev_oix_path) as prev_f:
#                     diff_tagged_routes, same_tagged_routes, ap_set, counter = generate_diff_same_tagged_routes_from_file_handler(cur_f, prev_f, remove_dup=remove_dup, remove_first=remove_first, mode=mode, test_limit=test_limit,
#                                                       asn_list=asn_list, ap_list=ap_list)
#
#         logging.info(("Extracted", len(ap_set), "aps from ", cur_oix_path))
#         logging.info(("Extracted", counter, "routes from ", cur_oix_path))
#         return diff_tagged_routes, same_tagged_routes, list(ap_set)
#
#
# def generate_diff_same_prev_dict_routes_from_oix(cur_oix_path, prev_oix_path, dt=None, remove_dup=False, mode=None,
#                                               test_limit=None, asn_list=None, ap_list=None):
#     def generate_diff_same_prev_dict_routes_from_file_handler(cur_f, prev_f, remove_dup=remove_dup, mode=mode,
#                                                            test_limit=test_limit,
#                                                            asn_list=asn_list, ap_list=ap_list):
#         ap_set = set()
#         diff_dict_routes = defaultdict(list)
#         prev_dict_routes = defaultdict(list)
#         same_dict_routes = defaultdict(list)
#         counter = 0
#         for i, line in enumerate(cur_f):
#             cur_line = line.split()
#             prev_line = prev_f.readline()
#             if len(cur_line) > 0 and cur_line[0] == '*':
#                 if mode != 'specific' or (asn_list and [asn for asn in asn_list if (asn in cur_line)]) \
#                         or (ap_list and [ap for ap in ap_list if (ap == cur_line[1])]):
#                     if remove_dup:
#                         if line == prev_line:
#                             same_dict_routes[cur_line[1]].append(remove_duplicates(cur_line[6:-1]))
#                         else:
#                             diff_dict_routes[cur_line[1]].append(remove_duplicates(cur_line[6:-1]))
#                             prev_line = prev_line.split()
#                             prev_dict_routes[prev_line[1]].append(remove_duplicates(prev_line[6:-1]))
#                     else:
#                         if line == prev_line:
#                             same_dict_routes[cur_line[1]].append(cur_line[6:-1])
#                         else:
#                             diff_dict_routes[cur_line[1]].append(cur_line[6:-1])
#                             prev_line = prev_line.split()
#                             prev_dict_routes[prev_line[1]].append(prev_line[6:-1])
#                     ap_set.add(cur_line[1])
#                     counter += 1
#             if mode == 'test' and counter >= test_limit:
#                 break
#         return diff_dict_routes, same_dict_routes, prev_dict_routes, ap_set, counter
#
#     if cur_oix_path == '-' or prev_oix_path == '-':
#         logging.critical(('There are no routes for dt', dt))
#         raise Exception
#     else:
#         logging.info(("Start generating diff and same tagged routes from ", cur_oix_path))
#         if cur_oix_path.endswith('.bz2'):
#             with bz2.open(cur_oix_path, "rt") as cur_f:
#                 with bz2.open(prev_oix_path, "rt") as prev_f:
#                     diff_dict_routes, same_dict_routes, prev_dict_routes, ap_set, counter = generate_diff_same_prev_dict_routes_from_file_handler(
#                         cur_f, prev_f, remove_dup=remove_dup, mode=mode, test_limit=test_limit,
#                         asn_list=asn_list, ap_list=ap_list)
#         else:
#             with open(cur_oix_path) as cur_f:
#                 with open(prev_oix_path) as prev_f:
#                     diff_dict_routes, same_dict_routes, prev_dict_routes, ap_set, counter = generate_diff_same_prev_dict_routes_from_file_handler(
#                         cur_f, prev_f, remove_dup=remove_dup, mode=mode, test_limit=test_limit,
#                         asn_list=asn_list, ap_list=ap_list)
#
#         logging.info(("Extracted", len(ap_set), "aps from ", cur_oix_path))
#         logging.info(("Extracted", counter, "routes from ", cur_oix_path))
#         return diff_dict_routes, same_dict_routes, prev_dict_routes, list(ap_set)
