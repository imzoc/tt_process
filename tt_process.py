import json
import pandas as pd

class Process_Json:
    def __init__(self, file_names_list, snippet=False):
        self.snippet = snippet
        self.file_names_list = file_names_list
    
    def flatten_dictionary(self, d, parent_key='', sep='/'):
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dictionary(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.extend(self.flatten_list(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def flatten_list(self, l, parent_key='', sep='/'):
        items = []
        for i, e in enumerate(l):
            new_key = parent_key + sep + str(i) if parent_key else str(i)
            if isinstance(e, dict):
                items.extend(self.flatten_dictionary(e, new_key, sep=sep).items())
            elif isinstance(e, list):
                items.extend(self.flatten_list(e, new_key, sep=sep).items())
            else:
                items.append((new_key, e))
        return dict(items)

    def tt_all_data_to_dataframe(self):
        # create the object we will convert into a dataframe
        df = {}

        # make a "fill_empty" function to fill the gaps between cases with a feature and cases
        # without that feature
        fill_empty = lambda x: ["NaN" for i in range(x)]

        # loop through files (usuall 48 of them), counting the case index.
        case_index = 0
        for file_name in self.file_names_list:
            # snippet functionality
            if self.snippet == True: cases = json.load(open(file_name, "r"))['results'][1:12]
            if self.snippet == False: cases = json.load(open(file_name, "r"))['results'][1:]

            # loop through cases in each file
            for case in cases:
                # generate a flat dictionary with useful keys
                flat = self.flatten_dictionary(case)

                # make select values of type int (maybe for k_prototypes?)
                if isinstance(flat["halstead_before"], int):
                    flat["halstead_before"] = int(flat["halstead_before"][30:])
                else:
                    flat["halstead_before"] = 0
                
                # "
                if isinstance(flat["halstead_after"], int):
                    flat["halstead_after"] = int(flat["halstead_after"][30:])
                else:
                    flat["halstead_after"] = 0
                
                # loop through key/value pairs in each case in each file
                for feature, value in flat.items():
                    # if a feature is not in df, we will create it.
                    if feature not in df: df.update({feature:[]})

                    # if the case before this one did not have this feature we need to fill the
                    # indexes between the last case with this feature and this case with "NaN".
                    furthest_case = len(df[feature])
                    if furthest_case < case_index: df[feature].extend(fill_empty(case_index - furthest_case))

                    # finally, after taking care of creating the feature if it doesn't exist and
                    # filling any unfilled values with "NaN", we can add the value.
                    df[feature].append("None") if value == "" else df[feature].append(value)

                case_index += 1
        # at the very end we have to fill any unfilled values with "NaN" so that df's values are
        # all of the same length.
        for key in df:
            furthest_case = len(df[key])
            if furthest_case < case_index: df[key].extend(fill_empty(case_index - furthest_case))

        # convert to dataframe and return.
        return pd.DataFrame.from_dict(df)
    def tt_output_df_to_csv(self, out_file_name, df="Blank"):
        if (df == "Blank"):
            pd.DataFrame(self.tt_all_data_to_dataframe()).to_csv(out_file_name)
        else:
            pd.DataFrame(df).to_csv(out_file_name)