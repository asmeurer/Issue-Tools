

# GCI-2011 Task list


The source if this page is based on the [google-malange](https://docs.google.com/spreadsheet/ccc?key=0AiMKW-ZM-_fedFpSWm51VFBFZkdTRnh3WkhYRndSVXc#gid=0) spreadsheet.

${'##'} Categories

<ul>
% for d in difficulties:
    % if d:
<li><a href="##${d}">${d}</a>
<ul>
        % for task in tasks.by_difficulty(d):
            % if task.Id:
<li><a href="##${task.Id}">${task.Summary}</a></li>
            % endif
         % endfor
</ul>
</li>
    % endif
% endfor
</ul>

% for d in difficulties:
${'##'} <a name="#${d}">${d}</a>
    % for task in tasks.by_difficulty(d):
        % if task.Id:
<a name="#${task.Id}"></a>
${'###'} [${task.Id}](http://code.google.com/p/sympy/issues/detail?id=${task.Id}&q=label%3ACodeInImportedIntoSpreadsheet) - ${task.Summary}
            % if task.Melange_Notes:
${task.Melange_Notes} 

            % endif
            % if task.description:

${task.description} 

            % endif
- *Category:* ${task.Categories}
            % if task.filtered_lables:
- *Labels:* ${task.filtered_lables}
            % endif
            % if task['Time to Complete (Hours)']:
- *Time to complete:* ${task['Time to Complete (Hours)']} hours
            %endif
            % if task['Additional Notes (to be put in Melange)']:

${task['Additional Notes (to be put in Melange)']} 
            % endif
<%
    mentors = task.mentors
    mentors = ['[%s](https://github.com/%s)' %(m['public_name'], m['github_nick']) for m in mentors]
    mentors_str = ", ".join(mentors)
%>
- *Mentors:* ${mentors_str}

        % endif
    % endfor
% endfor

${'##'} Links:
- [[GCI-2011 Landing]]
- [[GCI-2011 Mentors]]
- [CGI-2011 Task list (spreadsheet)](https://docs.google.com/spreadsheet/ccc?key=0AiMKW-ZM-_fedFpSWm51VFBFZkdTRnh3WkhYRndSVXc)
- [GCI-2011 Task list (wiki)](https://github.com/sympy/sympy/wiki/GCI-2011-Task-list)
- [[GCI-2011 Organization Application]]
