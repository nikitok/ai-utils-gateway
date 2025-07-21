{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "ui.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "directual.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- .Release.Name }}
{{- end -}}
{{- end -}}

{{- define "api-ws.fullname" -}}
{{- printf "api-%s" .Release.Name }}
{{- end -}}

{{- define "chart_prefix" -}}
{{- printf "%s-%s" .Chart.Name .Release.Name }}
{{- end -}}

{{- define "directual.external_domain" -}}
{{- printf "my.%s.%s" .Release.Name .Values.global.external_domain }}
{{- end -}}
{{- define "directual.external_domain_without_release" -}}
{{- printf "my.%s" .Values.global.external_domain }}
{{- end -}}
{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "ui.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "ui.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "ui.labels" -}}
helm.sh/chart: {{ include "ui.chart" . }}
{{ include "ui.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "ui.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ui.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "ui.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "ui.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Common labels for directual
*/}}
{{- define "directual.labels" -}}
helm.sh/chart: {{ include "ui.chart" . }}
{{ include "directual.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/component: frontend
app.kubernetes.io/part-of: directual
{{- end }}

{{/*
Selector labels for directual
*/}}
{{- define "directual.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ui.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use for directual
*/}}
{{- define "directual.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "directual.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
