

**Type**: 🧠 Fleeting Note  
**Created**: 2025-05-20 18:20  
**Tags**: #fleeting #inbox  
[[Zettelkasten OS v1 – Setup Notes]]

---

## Thought  
I want to grow my note garden and measure my growth. 
We will need dataview and obsidan charts
Requires a script

## Context  
Where did this come from? (Article, conversation, reflection, etc.)
- https://obsidian.rocks/a-graph-for-zettelkasten-measuring-growth-in-obsidian/
- ````
---
location: ''
daysback: 2
chartlength: 50
---
```dataviewjs
const start = moment();
const daysback = parseInt(dv.current().daysback) || 2;
const location = dv.current().location || '';
const dateField = 'created';
const chartColor = '#4e9a06';
const chartlength = parseInt(dv.current().chartlength) || 50;
const docs = dv.pages(location);

function getRecentDocs(numDays) {
    return docs
        .where(f => {
            if (!f[dateField] || !f[dateField].toISO) return false;
            var startDate = moment(start);
            var pastDate = startDate.subtract(numDays, 'days');
            var docDate = moment(f[dateField].toISO());
            return docDate.isAfter(pastDate) && docDate.isBefore(start);
        });
}

// creating the table
var ztDocs = getRecentDocs(daysback);

    dv.table(['link', 'date'], ztDocs
        .sort(a => a[dateField], 'desc')
        .map(b => [b.file.link, moment(b[dateField].toISO()).format('YYYY-MM-DD hh:mm')]));

// creating the charts
var ztLastWeek = getRecentDocs(chartlength).sort(f => f[dateField]);
var daysData = [];
var totalcount = 0;

// formatting the data
for (var i=0; i<=ztLastWeek.length; i++) {
    var f = ztLastWeek[i];
    if (f && f[dateField] && f[dateField].toISO) {
        var itemDate = moment(f[dateField].toISO());
        var newDate = itemDate.format('MM-DD');
        var index = daysData.findIndex(d => d.label === newDate);
        if (index !== -1) {
            daysData[index].num += 1;
        } else {
            daysData.push({label: newDate, num: 1});
        }
        totalcount += 1;
    }
};

var labels = [],
    data = [],
    aggData = [];

daysData.map(el => {
    labels.push(el.label);
    data.push(el.num);

    if (aggData.length) {
        var lastNum = aggData[aggData.length - 1];
        aggData.push(el.num + lastNum);
    } else {
        aggData.push(el.num);
    }
});

const lineChart = {
    type: 'line',
    data: {
    labels: labels,
    datasets: [{
        label: 'Docs created',
        data: data,
        backgroundColor: [
            chartColor
        ],
        borderColor: [
            chartColor
        ],
        borderWidth: 1
    }]
   }
}

const aggregateChart = {
    type: 'line',
    data: {
        labels: labels,
        datasets: [{
            label: 'Aggregate Docs Created',
            data: aggData,
            backgroundColor: [
                chartColor
            ],
            borderColor: [
                chartColor
            ],
            borderWidth: 1
        }]
    }
}

window.renderChart(lineChart, this.container);
window.renderChart(aggregateChart, this.container);

dv.paragraph('Total: ' + totalcount);
```
````

