<div style="position:absolute;
					    top:50%;
					    right:0;
					    left:45%;">
<form action="/" method="get">
	<input type="text" name="keywords">
	<input type="submit" name="submit" value="submit">
</form>

<strong>Results: (Descending Counts then Ascending Alphabets)</strong>
<table id="results">
%for keyword in results:
	<tr>
		<td>{{keyword[0]}}</td>
		<td>{{keyword[1]}}</td>
	</tr>
%end
</table>

<strong>History: (Descending Counts then Ascending Alphabets)</strong>
<table id="history">
%for keyword in history:
	<tr>
		<td>{{keyword[0]}}</td>
		<td>{{keyword[1]}}</td>
	</tr>
%end
</table>
