CREATE TABLE "Partner" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "key" varchar,
  "domain_name" varchar,
  "date" date,
  "sort_order" integer,
  "created_at" date,
  "updated_at" date
);

CREATE TABLE "Provider" (
  "provider_id" varchar,
  "name" varchar,
  "created_at" date,
  "updated_at" date
);

CREATE TABLE "PartnerProvider" (
  "partner" integer,
  "provider" integer
);

CREATE TABLE "Brand" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "alias" varchar,
  "key" varchar,
  "date" date,
  "sort_order" integer,
  "created_at" date,
  "updated_at" date,
  "partners" integer
);

CREATE TABLE "BrandsPartners" (
  "brand" integer,
  "partner" integer
);

CREATE TABLE "BrandsProviders" (
  "brand" integer,
  "provider" integer
);

CREATE TABLE "Location" (
  "id" integer,
  "country_code" varchar,
  "country" varchar
);

CREATE TABLE "PropertyGroup" (
  "id" integer,
  "name" varchar,
  "created_at" date,
  "updated_at" date
);

CREATE TABLE "PropertyCategory" (
  "id" integer,
  "name" varchar,
  "group" integer
);

CREATE TABLE "PropertyType" (
  "id" integer,
  "name" varchar,
  "brand" integer,
  "created_at" date,
  "updated_at" date
);

CREATE TABLE "PartnerPropertyType" (
  "id" integer,
  "name" varchar,
  "partner" integer,
  "created_at" date,
  "updated_at" date
);

CREATE TABLE "PartnerPropertyMapping" (
  "property_type" integer,
  "partner_property" integer
);

CREATE TABLE "Device" (
  "id" integer,
  "type" varchar,
  "sort_order" integer,
  "created_at" date,
  "updated_at" date
);

CREATE TABLE "BrandLocationPartnerProperty" (
  "id" integer,
  "brand" integer,
  "location" integer,
  "partner" integer,
  "property_group" integer,
  "device" integer,
  "providers" integer
);

CREATE TABLE "BrandLocationPartnerPropertyProvider" (
  "loc" integer,
  "provider" integer,
  "order" integer,
  "status" integer,
  "created_at" date,
  "updated_at" date
);

ALTER TABLE "PartnerProvider" ADD FOREIGN KEY ("partner") REFERENCES "Partner" ("id");

ALTER TABLE "PartnerProvider" ADD FOREIGN KEY ("provider") REFERENCES "Provider" ("provider_id");

CREATE TABLE "Partner_Brand" (
  "Partner_id" integer,
  "Brand_partners" integer,
  PRIMARY KEY ("Partner_id", "Brand_partners")
);

ALTER TABLE "Partner_Brand" ADD FOREIGN KEY ("Partner_id") REFERENCES "Partner" ("id");

ALTER TABLE "Partner_Brand" ADD FOREIGN KEY ("Brand_partners") REFERENCES "Brand" ("partners");


ALTER TABLE "BrandsPartners" ADD FOREIGN KEY ("brand") REFERENCES "Brand" ("id");

ALTER TABLE "BrandsPartners" ADD FOREIGN KEY ("partner") REFERENCES "Partner" ("id");

ALTER TABLE "BrandsProviders" ADD FOREIGN KEY ("brand") REFERENCES "Brand" ("id");

ALTER TABLE "BrandsProviders" ADD FOREIGN KEY ("provider") REFERENCES "Provider" ("provider_id");

ALTER TABLE "PropertyCategory" ADD FOREIGN KEY ("group") REFERENCES "PropertyGroup" ("id");

ALTER TABLE "PropertyType" ADD FOREIGN KEY ("brand") REFERENCES "Brand" ("id");

ALTER TABLE "PartnerPropertyType" ADD FOREIGN KEY ("partner") REFERENCES "Partner" ("id");

ALTER TABLE "PartnerPropertyMapping" ADD FOREIGN KEY ("property_type") REFERENCES "PropertyType" ("id");

ALTER TABLE "PartnerPropertyMapping" ADD FOREIGN KEY ("partner_property") REFERENCES "PartnerPropertyType" ("id");

ALTER TABLE "BrandLocationPartnerProperty" ADD FOREIGN KEY ("brand") REFERENCES "Brand" ("id");

ALTER TABLE "BrandLocationPartnerProperty" ADD FOREIGN KEY ("location") REFERENCES "Location" ("id");

ALTER TABLE "BrandLocationPartnerProperty" ADD FOREIGN KEY ("partner") REFERENCES "Partner" ("id");

ALTER TABLE "BrandLocationPartnerProperty" ADD FOREIGN KEY ("property_group") REFERENCES "PropertyGroup" ("id");

ALTER TABLE "BrandLocationPartnerProperty" ADD FOREIGN KEY ("device") REFERENCES "Device" ("id");

CREATE TABLE "Provider_BrandLocationPartnerProperty" (
  "Provider_provider_id" varchar,
  "BrandLocationPartnerProperty_providers" integer,
  PRIMARY KEY ("Provider_provider_id", "BrandLocationPartnerProperty_providers")
);

ALTER TABLE "Provider_BrandLocationPartnerProperty" ADD FOREIGN KEY ("Provider_provider_id") REFERENCES "Provider" ("provider_id");

ALTER TABLE "Provider_BrandLocationPartnerProperty" ADD FOREIGN KEY ("BrandLocationPartnerProperty_providers") REFERENCES "BrandLocationPartnerProperty" ("providers");


ALTER TABLE "BrandLocationPartnerPropertyProvider" ADD FOREIGN KEY ("loc") REFERENCES "BrandLocationPartnerProperty" ("id");

ALTER TABLE "BrandLocationPartnerPropertyProvider" ADD FOREIGN KEY ("provider") REFERENCES "Provider" ("provider_id");
