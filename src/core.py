import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import seaborn as sns
from IPython.display import display
import matplotlib
import os
from IPython.core.display import HTML

def _css(fileName='../css/custom.css'):
    style = open(fileName, "r").read()
    return HTML(style)

def _rc():
    pd.set_option('display.float_format', lambda x: '%.3f' % x)
    rc={'font.size': 22, 'axes.labelsize': 22, 'legend.fontsize': 22.0, 
        'axes.titlesize': 22, 'xtick.labelsize': 12, 'ytick.labelsize': 16,
        'legend.fontsize': 15.0, 'figure.figsize': [15, 8]}
    plt.rcParams.update(**rc)
    sns.set(style='white', rc=rc)

def configure(configType):
    if configType == 'css':
        _css()
    elif configType == 'rc':
        _rc()

class BaseballModel:
    def __init__(self, ROOT):
        self._salary = os.path.join(ROOT, 'Salaries.csv')
        self._master = os.path.join(ROOT, 'Master.csv')
        self._teams = os.path.join(ROOT, 'Teams.csv')
        self._batting = os.path.join(ROOT, 'Batting.csv')
        self._pitching = os.path.join(ROOT, 'Pitching.csv')
        self.bat = self.clean_batting(self._batting)
        self.pitch = self.clean_batting(self._pitching)

    @property
    def salary(self):
        return pd.read_csv(self._salary)
    @property
    def master(self):
        return pd.read_csv(self._master)
    @property
    def teams(self):
        return pd.read_csv(self._teams).dropna()
    
    def clean_batting(self, dataframe):
        temp = pd.read_csv(dataframe)
        temp = temp[temp.yearID >= 1985]
        return temp.fillna(0).reset_index().drop('index', axis=1);
    
    @property
    def batting(self):
        return self.bat
    
    @property
    def pitching(self):
        return self.pitch

    @staticmethod
    def performance_burndown(dataframe):
        plot_data = dataframe.groupby('yearID', as_index=False).sum()
        g = sns.PairGrid(plot_data, 
                     x_vars=['R', 'HR', 'RBI', 'CS', 'SO'], y_vars=["yearID"], 
                     size=10, aspect=.3)
        # # # Draw a dot plot using the stripplot function
        g.map(sns.stripplot, size=12, orient="h",
              palette="Reds_d", edgecolor="red")
        g.set(xlabel="performance", ylabel="")
        titles = ["Total Runs", "Home runs", "Runs Batted In", 
              "Caught Stealing", "Strikeouts"]
        for ax, title in zip(g.axes.flat, titles):
            # Set a different title for each axes
            ax.set(title=title)
            # # # Make the grid horizontal instead of vertical
            ax.xaxis.grid(False)
            ax.yaxis.grid(True)
        sns.despine(left=True, bottom=True)
        plt.show()

    @staticmethod
    def create_descriptive_pie(dataframe, hue, columns, tags,
                          ncol=3, nrow=2):
        labels = list(dataframe[hue].unique())
        matplotlib.style.use('fivethirtyeight')
        # TODO This part could be more generic
        df1 = dataframe[dataframe[hue] == labels[0]]
        df2 = dataframe[dataframe[hue] == labels[1]]
    #     print(labels)
        fig, ax = plt.subplots(nrow, ncol);
        explode = (0, 0.3)
        for row in range(nrow):
            for col in range(ncol):
                size = [df1[columns[col + (row * ncol)]].sum(), 
                        df2[columns[col + (row * ncol)]].sum()]
    #             print(columns[col + (row * ncol)], size)
                ax[row][col].pie(size, explode=explode, autopct='%1.1f%%',
                             shadow=True, startangle=90,
                             colors=['#A1CAF1', '#FF947B']);
                ax[row][col].axis('equal');
                ax[row][col].set_xlabel(tags[col + (row * ncol)], 
                                        fontweight='bold',
                                        fontsize=19);
        plt.legend(labels, loc=(1, 1));
        plt.show();

    def prepare_heatmap_data(self, data_1, their_clubs, tc):
        from operator import itemgetter
        heatmap_salary_data = pd.DataFrame(index=list(their_clubs.keys()), 
                                    columns={*map(itemgetter(1), tc)})
        heatmap_tenure_data = pd.DataFrame(index=list(their_clubs.keys()), 
                                    columns={*map(itemgetter(1), tc)})
        heatmap_Pindex_data = pd.DataFrame(index=list(their_clubs.keys()), 
                                    columns={*map(itemgetter(1), tc)})
        heatmap_sArrow_data = pd.DataFrame(index=list(their_clubs.keys()), 
                                    columns={*map(itemgetter(1), tc)})
        heatmap_mArrow_data = pd.DataFrame(index=list(their_clubs.keys()), 
                                    columns={*map(itemgetter(1), tc)})
        for player, clubs in their_clubs.items():
            for club in clubs:
                d =  data_1[(data_1.teamID == club)&
                            (data_1.fullName == player)]
                heatmap_salary_data.loc[player, club] = d.salary.sum() / 1000000.0
                heatmap_tenure_data.loc[player, club] = d.yearID.max() - d.yearID.min()
                temp = data_1[(data_1.yearID <= d.yearID.max()) &
                               (data_1.yearID >= d.yearID.min())]
                gp_score = (d.G / temp.G.std()).sum()
                rs_score = (d.Runs_Scored / temp.Runs_Scored.std()).sum()
                hr_score = (d.HR_Scored / temp.HR_Scored.std()).sum()
                sho_score = (d.SHO / temp.SHO.std()).sum()
                sv_score = (d.SV / temp.SV.std()).sum()
                heatmap_Pindex_data.loc[player, club] = gp_score + rs_score + \
                                                        hr_score + sho_score + \
                                                        sv_score
                gTemp = temp.groupby('fullName', as_index=False)['salary'].sum()
                gTemp.sort_values('salary', ascending=False, inplace=True)
                if player in list(gTemp.head().fullName):
                    heatmap_sArrow_data.loc[player, club] = '▲'
                else:
                    heatmap_sArrow_data.loc[player, club] = '▼'

                metrics = ['G', 'Runs_Scored', 'HR_Scored', 'SHO', 'SV']
                gTemp = temp.groupby('fullName', as_index=False)[metrics].sum()
                gTemp['G'] /= temp.G.std()
                gTemp['Runs_Scored'] /= temp.Runs_Scored.std()
                gTemp['HR_Scored'] /= temp.HR_Scored.std()
                gTemp['SHO'] /= temp.SHO.std()
                gTemp['SV'] /= temp.SV.std()
                gTemp['Gross_Metric_Score'] = gTemp['G'] + \
                    gTemp['Runs_Scored'] + gTemp['HR_Scored'] + \
                    gTemp['SHO'] + gTemp['SV']
                gTemp.sort_values('Gross_Metric_Score', ascending=False, inplace=True)
                if player in list(gTemp.head().fullName):
                    heatmap_mArrow_data.loc[player, club] = '▲'
                else:
                    heatmap_mArrow_data.loc[player, club] = '▼'

        heatmap_salary_data.fillna(0, inplace=True)
        heatmap_tenure_data.fillna(0, inplace=True)
        heatmap_Pindex_data.fillna(0, inplace=True)
        heatmap_sArrow_data.fillna(0, inplace=True)
        heatmap_mArrow_data.fillna(0, inplace=True)

        heatmap_data = heatmap_salary_data.applymap(str) + '_' \
                     + heatmap_tenure_data.applymap(str) + '_' \
                     + heatmap_Pindex_data.applymap(str) + '_' \
                     + heatmap_sArrow_data.applymap(str) + '_' \
                     + heatmap_mArrow_data.applymap(str)
        return heatmap_data, heatmap_salary_data
    
    @staticmethod
    def create_categorical_heatmap(heatmap_meta):
        heatmap_data = heatmap_meta[0]
        heatmap_salary_data = heatmap_meta[1]
        column_labels = list(heatmap_data.index.values)
        row_labels = list(heatmap_data.columns.values)
        fig, ax = plt.subplots()
        heatmap = ax.imshow(np.array(heatmap_salary_data)
                            ,cmap='GnBu'
                            ,interpolation='spline36')
        ax.invert_yaxis()
        ax.xaxis.tick_top()
        ax.set_xticks(np.arange(len(row_labels)))
        ax.set_yticks(np.arange(len(column_labels)))

        ax.set_xticklabels(row_labels, minor=False)
        ax.set_yticklabels(column_labels, minor=False)

        for y in range(heatmap_data.shape[0]):
            for x in range(heatmap_data.shape[1]):
                data = heatmap_data.iloc[y, x].split('_')
                if float(data[0]) and not int(data[1]): 
                    data[1] = '< 1'
                label_salary = '{:.2f}M'.format(float(data[0]))
                label_years = '\n{} yrs'.format(data[1])
                label_score = '\n{:.3f}'.format(float(data[2]))

                if heatmap_salary_data.iloc[y, x] <= 120 and \
                heatmap_salary_data.iloc[y, x] != 0:
                    plt.text(x, y, label_salary + data[3] + label_score + data[4] + label_years,
                         horizontalalignment='center',
                         verticalalignment='center',
                         fontsize=15, 
                         color='black',
                         fontweight='bold')
        #             print(label_salary + data[3] + label_years + label_score)
                elif heatmap_salary_data.iloc[y, x] > 120 and \
                heatmap_salary_data.iloc[y, x] != 0:
                     plt.text(x, y, label_salary + data[3] + label_score + data[4] + label_years,
                         horizontalalignment='center',
                         verticalalignment='center',
                         fontsize=15, 
                         color='white',
                         fontweight='bold')
        #              print(label_salary + data[3] + label_years + label_score)
                else:
                    plt.text(x, y, label_salary + label_years \
                             + label_score,
                         horizontalalignment='center',
                         verticalalignment='center',
                         fontsize=14, 
                         color='red')
        fig.text(0.5, 0.865, 'Top 5 player\'s Career Satistics',
             horizontalalignment='center', color='black', weight='bold',
             size='large')
        plt.show()
