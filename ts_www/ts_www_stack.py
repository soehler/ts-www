from aws_cdk import (
     core,
     aws_s3 as s3_,
     aws_s3_deployment as s3deploy_,
     aws_cloudfront as clf_,
     aws_certificatemanager as cm_,
     aws_route53 as r53_,
     aws_route53_targets as r53tgs_
)

class TsWwwStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str,domain_name:str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Materialize existing AWS Hosted DNS Zone
        dns_zone = r53_.HostedZone.from_lookup(self,"dns_zone",domain_name = domain_name)
        
        # Compose site name for AWS Certificate
        site_fqdn = "www." + dns_zone.zone_name

        # Create a DNS Certificate
        certificate = cm_.DnsValidatedCertificate (self,"certificate",
                                                         domain_name=site_fqdn,
                                                         hosted_zone=dns_zone,
                                                         region="us-east-1")

        # Define Bucket to store Site Contents
        ts_www_bucket = s3_.Bucket(self,"truesys-static-website",
                                        bucket_name = site_fqdn,
                                        website_index_document = "index.html",
                                        website_error_document = "404/index.html",
                                        public_read_access = True
                                        )

        #Cria lambda function para fazr URL Rewriting de default document
        url_rewrite_lambda = _lambda.Function(self,'URLRewriteLambdaEdge',
                                                   handler='url_rewrite_handler.handler',
                                                   runtime=_lambda.Runtime.PYTHON_3_7,
                                                   code=_lambda.Code.asset('lambda_edge'),
        )
        
        
        // A numbered version to give to cloudfront
       const myOriginRequestHandlerVersion = new lambda.Version(this, "OriginRequestHandlerVersion", {
               lambda: myOriginRequestHandler,
});
        
        
        lea = clf_.AlambdaFunctionAssociation(event_type = cfl_AlambdaEdgeEventType.ORIGIN_REQUEST, myOriginRequestHandlerVersion)
        
        #Define Cloud Front distribution
        s3_origin_config = clf_.S3OriginConfig(s3_bucket_source = ts_www_bucket)
        behaviour = clf_.Behavior(is_default_behavior=True, 
                                  lambda_function_associations = [lea])
        source_config = clf_.SourceConfiguration(s3_origin_source=s3_origin_config,
                                                 behaviors = [behaviour])
        clf_alias_config = clf_.AliasConfiguration(acm_cert_ref = certificate.certificate_arn,
                                                  names=[site_fqdn], 
                                                  ssl_method = clf_.SSLMethod.SNI,
                                                  security_policy = clf_.SecurityPolicyProtocol.TLS_V1_1_2016)
        cf_distribution = clf_.CloudFrontWebDistribution(self,"TsDistribution",
                                                           origin_configs=[source_config],
                                                           alias_configuration=clf_alias_config,
                                                           price_class = clf_.PriceClass.PRICE_CLASS_ALL
                                                     )
                                                     
        #Define Route 53 Alias aka endereco do site
        cloud_front_target = r53tgs_.CloudFrontTarget(distribution = cf_distribution) 
        r53_target = r53_.RecordTarget.from_alias(alias_target = cloud_front_target)
        r53_.ARecord(self,"EnderecoDosite",record_name = site_fqdn,
                                           target = r53_target,
                                           zone = dns_zone)
        
        
        #Faz deploy do conteudo do site para o S3 e invalida distribution
        site_assets = s3deploy_.Source.asset("./true-systems-static-site/public")
        s3deploy_.BucketDeployment(self,"truesys-website-content-deployment",
                                        sources = [site_assets],
                                        destination_bucket=ts_www_bucket,
                                        distribution=cf_distribution,
                                        distribution_paths = [ "/*"])

        core.CfnOutput(self,"Site",value = site_fqdn)                                

