TARRIFICARTOR_ADR = """
@startuml
!theme toy
scale 2

participant "ATS.hr-crm-api" as ats
participant "WBTeam.cmr-api" as crm
participant "CustomFields.Service" as customfields
participant "Tarificator.API" as trf
participant "OrgStruct.Service" as org
participant "NATS" as nats

group ATS
        ats -> ats: Every 20 minutes a task to update candidate's salary is launched
        ats -> ats: Get all candidates who are not registered in WBTeam with the status "Processed/Working"
 is_registered_in_wbteam=false

        loop for all candidates
                ats -> ats: Set CalculationType = "IT department"
		            ats -> ats: Set MotivationType = "Undefined"
                ats -> ats: Set the candidate's flag that he is registered in WBTeam
 set is_registered_in_wbteam=true
                ats -> crm: Request CRM to update candidate's salary in WBTeam
/api/v1/create_income_for_hr_crm_api


                group CRM-API
                        crm -> crm: Search for a user by WBUserID or by (Fio AND Phone)
                        crm -> customfields: Request CustomFields service to save motivation type in custom fields
                        group CustomFields
                                customfields -> customfields: Save motivation type in custom fields
                                customfields -[#red]-> customfields: "<font color=red> Commit all changes</font>"
                        end
                        crm -> trf: Request tariff calculator to save CalculationType
 /api/v1/pub/calculation-type

                        group Tarificator
                                alt if request type is not equal to 0
                                        trf -> trf: Add or update CalculationType
 in tariff_office.employee_fields
                                else
                                        trf -> trf: Search for calculation type in custom_fields table
                                        alt if there is no record
                                                trf -> trf: Add a record to the custom_fields table
                                                trf -> trf: Get the ID of CalculationType that came from the request
 tariff_office.calculation_type
                                                trf -> trf: Add or update CalculationType
 tariff_office.employee_fields
                                        end
                                        trf -> trf: Update CalculationType in custom_fields table
                                        trf -> trf: Get the ID of CalculationType that came from the request
 tariff_office.calculation_type
                                        trf -> trf: Add or update CalculationType
 tariff_office.employee_fields
                                end
                                trf -[#red]-> trf: "<font color=red> Commit all changes</font>"
                        end

                        crm -> crm: Search for RECRUITER by WBUserID or by (Fio AND Phone)
                        crm -> crm: Save salary for an dailymeetinglog with the status `send_to_tarificator`
 employee_income.income
                        note over crm
                                This is called SalaryApproval.
                                The last action occurs in an atomic transaction
                                in case of rollback of the main transaction - salary change will not rollback
                        end note

                        crm -> trf: Update salary in the tariff calculator
 /api/v1/pub/incomes
                        note over crm
                                Send attributes:
                                IsBonus:         false
                                IsNewEmployee:   true,
                                ApplicationDate: time.Now(),
                        end note
                        group Tarificator

                                == update salary tariff_office.incomes ==
                                trf -> trf: Check if the service(hr-crm-api) is in the available services
                                alt no service
                                        trf -> trf: Make the current active salary inactive
                                        trf -> trf: Add a new active salary
                                else service exists
                                        trf -> trf: Make the current active salary inactive
                                        trf -> trf: Update all records of active salaries for the service(hr-crm-api) to new values
                                        note over trf
                                                It's not clear here. Update everything!!!
	                                              queryUpdate := `UPDATE tariff_office.incomes SET total_sum = $1, current_sum = $2, is_current = $4 WHERE income_service_id = $3`
                                        end note
                                end
                                trf -[#red]-> trf: "<font color=red> Commit all changes</font>"


                                == enable dailymeetinglog calculation and payment ==
                                note over trf
                                        Important - the dailymeetinglog is new!
                                end note
                                trf -> trf: Set the `calculation` and `payment` flags to true
 tariff_office.access_users
                                trf -> trf: Set the status of accruals - recalculate from the specified date
 `ready_for_billing` if the status is `do_not_pay` and date >= specified value
 tariff_office.accruals
                                note over trf
                                        For new employees there are no records!!!
                                        We won't update anything
                                end note

                                trf -> trf: Set the status of accruals - do not pay until the specified date
 `do_not_pay` if the status is `ready_for_billing` and date < specified value
 tariff_office.accruals

                                trf -> trf: Delete canceled accruals
 status=`cansel` AND date >=specified value
                                trf -[#red]-> trf: "<font color=red> Commit all changes</font>"

                                == Delete ready accruals ==
                                group #tomato do atomically, without the possibility to rollback changes
                                        trf -> trf: Delete all errors that occurred during payments
all history
                                end

                                group #tomato do atomically, without the possibility to rollback changes
                                        trf -> trf: Delete all accruals that are ready for payment from the specified date
 status = `ready_for_billing`
                                end

                                trf -> nats: Send a message to Tarificator.CALC for recalculation

                        end

                        crm -> org: Request to embed the user in the org-structure

                        group ORG-STRUCT-API
                                org -> org: Add or update group-dailymeetinglog relationship
                                org -[#red]-> org: "<font color=red> Commit all changes</font>"
                        end

                end

        end
        ats -> ats: Commit the transaction
end

@enduml

"""

ROUTES = """
package handlers

import (
	"context"
	"io"

	"github.com/buaazp/fasthttprouter"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/rs/zerolog"
	"github.com/valyala/fasthttp"
	"github.com/valyala/fasthttp/fasthttpadaptor"
	"gitlab.wildberries.ru/hr/hr/scans/internal/document"
	"gitlab.wildberries.ru/hr/hr/scans/internal/mid"
)

type service interface {
	UploadDocuments(ctx context.Context, doc *document.EmployeeFiles) (document.OldNewFilenames, error)
	DownloadTo(ctx context.Context, employeeID string, fileName string, w io.Writer) error
	DownloadManyTo(ctx context.Context, fileName string, w io.Writer, employeeIDs ...string) error
	DownloadBinaryTo(ctx context.Context, employeeID string, fileName string, w io.Writer) error
	List(ctx context.Context, employeeID string) (*document.FileList, error)
	Delete(ctx context.Context, employeeID string, filename string) error
	DocumentsSync(ctx context.Context, emplID int, worksheetID int, isApproved *bool) (document.Information, error)
}

type handler struct {
	svc    service
	logger *zerolog.Logger
}

// API - api router handler
func API(svc service, authmw *mid.Auth, pr prober, logger *zerolog.Logger) func(ctx *fasthttp.RequestCtx) {
	router := fasthttprouter.New()

	h := health{p: pr, log: logger}
	router.GET("/alive", h.alive)
	router.GET("/ready", h.ready)

	hdl := handler{svc: svc, logger: logger}

	// для 1С
	router.GET("/v1/documents/:id", authmw.OneCCheck(hdl.List))
	router.GET("/v1/documents/:id/*filename", authmw.OneCCheck(hdl.Download))
	router.POST("/v1/documents", authmw.OneCCheck(hdl.UploadFor1C))
	router.DELETE("/v1/documents/:id/:filename", authmw.OneCCheck(hdl.Delete))

	// не все могут (внутренние)
	router.GET("/v1/photo/:id", authmw.EmployeeValidate(hdl.GetPhoto))
	router.GET("/v1/preview/:id", authmw.EmployeeValidate(hdl.GetPreview))
	router.GET("/v1/photo", authmw.EmployeeValidate(hdl.GetPhotoList))
	router.GET("/v1/preview", authmw.EmployeeValidate(hdl.GetPreviewList))

	// внутренние пользовательские
	router.GET("/sc/v2/photo/:id", authmw.EmployeeValidate(hdl.GetPhotoV2))
	router.GET("/sc/v2/preview/:id", authmw.EmployeeValidate(hdl.GetPreviewV2))

	// для мобилки
	router.GET("/sc/employees/preview/:id", authmw.EmployeeValidate(hdl.GetPreviewV2))

	// ручки, которые дергают другие сервисы, а не сотрудники
	router.POST("/sc/v1/documents/syncs", authmw.TokenCheck(hdl.Sync))
	router.POST("/sc/v2/out/documents", authmw.ServiceHasRoles(hdl.UploadForService, "document.upload"))

	// legacy ручки для получения фотографий и их превью сервисами
	router.GET("/v1/out/photo/:id", authmw.ServiceHasRoles(hdl.GetPhoto, "photo.read"))
	router.GET("/v1/out/preview/:id", authmw.ServiceHasRoles(hdl.GetPreview, "photo.read"))
	router.GET("/v1/out/photo", authmw.ServiceHasRoles(hdl.GetPhotoList, "photo.read"))
	router.GET("/v1/out/preview", authmw.ServiceHasRoles(hdl.GetPreviewList, "photo.read"))

	// ручки для получения фотографий и их превью сервисами
	router.GET("/sc/v2/out/photo/:id", authmw.ServiceHasRoles(hdl.GetPhotoV2, "photo.read"))
	router.GET("/sc/v2/out/preview/:id", authmw.ServiceHasRoles(hdl.GetPreviewV2, "photo.read"))

	return log_http(router.Handler)
}

// Metrics - metrics router handler
func Metrics() func(ctx *fasthttp.RequestCtx) {
	router := fasthttprouter.New()
	prometeus := fasthttpadaptor.NewFastHTTPHandler(promhttp.Handler())
	router.GET("/metrics", prometeus)
	return router.Handler
}

func log_http(next fasthttp.RequestHandler) fasthttp.RequestHandler {
	return func(ctx *fasthttp.RequestCtx) {
		next(ctx)
		ctx.Logger().Printf("%d: %d bytes", ctx.Response.StatusCode(), len(ctx.Response.Body()))
	}
}
"""

ROUTES_DESCRIPTION = """
The flow-overview diagram illustrates the operations of a Golang microservice architecture for handler routes. This microservice is designed to handle various types of requests related to documents such as uploading, downloading, listing, and deleting documents. It also includes routes for health checks and metrics.

The process starts with the initialization of the API and Metrics router handlers. The API router has various routes defined for interacting with documents:

1. The "/alive" and "/ready" routes are used for health checks, to ensure the service is up and running.

2. Routes "/v1/documents/:id" and "/v1/documents/:id/*filename" are used for listing and downloading documents respectively. These routes are authenticated using the OneCCheck middleware.

3. Route "/v1/documents" is used for uploading documents, and "/v1/documents/:id/:filename" is used for deleting documents. Both routes are authenticated using the OneCCheck middleware.

4. The routes "/v1/photo/:id", "/v1/preview/:id", "/v1/photo", and "/v1/preview" are used for getting photo and preview information. These routes are authenticated using the EmployeeValidate middleware.

5. The routes "/sc/v2/photo/:id" and "/sc/v2/preview/:id" are used for getting version 2 of photo and preview information. These routes are authenticated using the EmployeeValidate middleware.

6. For mobile requests, route "/sc/employees/preview/:id" is used to get preview information, authenticated using the EmployeeValidate middleware.

7. The routes "/sc/v1/documents/syncs" and "/sc/v2/out/documents" are used by other services for document synchronization and upload respectively. These routes are authenticated using TokenCheck and ServiceHasRoles middleware.

8. Legacy routes "/v1/out/photo/:id", "/v1/out/preview/:id", "/v1/out/photo", and "/v1/out/preview" are used for getting photo and preview information by services. These routes are authenticated using the ServiceHasRoles middleware.

9. The routes "/sc/v2/out/photo/:id" and "/sc/v2/out/preview/:id" are used for getting version 2 of photo and preview information by services. These routes are authenticated using the ServiceHasRoles middleware.

In addition to these, there is a "/metrics" route under the Metrics router handler, which is used for monitoring performance metrics of the microservice.

This diagram provides a clear understanding of the microservice's behavior and can be used as a guide for implementing similar systems.
"""